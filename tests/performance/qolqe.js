// Pruebas de rendimiento de Qolqe Wallet con k6 — requerimiento "Quincena Qolqe".
// Uso: k6 run -e ESCENARIO=carga|pico|estres|resistencia tests/performance/qolqe.js
// (lo normal es lanzarlo con ejecutar.py, que prepara datos, mide CPU/memoria y analiza).
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Counter } from 'k6/metrics';
import exec from 'k6/execution';

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const ESCENARIO = __ENV.ESCENARIO || 'carga';
const N_USUARIOS = Number(__ENV.N_USUARIOS || 600);
const PIN = '2580';

// Etapas de cada escenario: [duración en s, VUs objetivo, etiqueta]. Origen de cada valor: README de la Parte 3.
//  - 3000 sesiones/h × 120 s/sesión ÷ 3600 s/h = 100 usuarios simultáneos en hora punta (ley de Little).
//  - Campaña: el triple = 300, con la mayoría entrando en los primeros 5 min; la ventana dura 15 min (12:00-12:15).
const ETAPAS = {
  carga: [[120, 100, 'rampa'], [600, 100, 'estable'], [60, 0, 'bajada']],
  pico: [[300, 300, 'rampa'], [600, 300, 'estable'], [60, 0, 'bajada']],
  estres: [], // se arma abajo: escalones de 200 VUs
  resistencia: [[120, 100, 'rampa'], [1800, 100, 'estable'], [60, 0, 'bajada']],
  humo: [[10, 2, 'rampa'], [40, 2, 'estable'], [5, 0, 'bajada']],
  demo: [[20, 50, 'rampa'], [60, 50, 'estable'], [10, 0, 'bajada']], // demo en vivo (~1.5 min)
};
// Escalones de 200 VUs por encima de la campaña (300) hasta encontrar dónde deja de cumplir.
const ESCALONES = (__ENV.ESCALONES || '200,400,600,800,1000,1200,1400,1600').split(',').map(Number);
for (const vus of ESCALONES) {
  ETAPAS.estres.push([60, vus, `r${vus}`]);   // subir al siguiente escalón
  ETAPAS.estres.push([120, vus, `${vus}`]);   // sostenerlo (más que una sesión completa de ~105 s)
}
ETAPAS.estres.push([60, 0, 'bajada']);

const etapas = ETAPAS[ESCENARIO];
const umbrales = {
  error_tecnico: ['rate<0.01'],
  'http_req_duration{tipo:consulta,etapa:estable}': ['p(95)<800'],
  'http_req_duration{tipo:dinero,etapa:estable}': ['p(95)<1500'],
};
if (ESCENARIO === 'estres') {
  delete umbrales['http_req_duration{tipo:consulta,etapa:estable}'];
  delete umbrales['http_req_duration{tipo:dinero,etapa:estable}'];
  for (const vus of ESCALONES) {  // un umbral por escalón: así se ve en qué nivel deja de cumplir
    umbrales[`http_req_duration{tipo:consulta,etapa:${vus}}`] = ['p(95)<800'];
    umbrales[`http_req_duration{tipo:dinero,etapa:${vus}}`] = ['p(95)<1500'];
    umbrales[`error_tecnico{etapa:${vus}}`] = ['rate<0.01'];
  }
}

export const options = {
  scenarios: {
    [ESCENARIO]: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: etapas.map(([s, vus]) => ({ duration: `${s}s`, target: vus })),
      gracefulRampDown: '30s',
      gracefulStop: '30s',
    },
  },
  thresholds: umbrales,
  summaryTrendStats: ['avg', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

// Errores técnicos (5xx, timeouts, conexión rechazada) frente a errores de negocio (4xx = problema de datos).
const errorTecnico = new Rate('error_tecnico');
const errorNegocio = new Counter('error_negocio');

function etapaActual() {
  let t = (Date.now() - exec.scenario.startTime) / 1000;
  for (const [s, , nombre] of etapas) {
    if (t < s) return nombre;
    t -= s;
  }
  return 'bajada';
}

function llamar(metodo, ruta, cuerpo, token, op, tipo) {
  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { op, tipo, etapa: etapaActual(), name: op },
  };
  if (token) params.headers.Authorization = `Bearer ${token}`;
  const r = http.request(metodo, `${BASE}${ruta}`, cuerpo ? JSON.stringify(cuerpo) : null, params);
  const tecnico = r.status === 0 || r.status >= 500;
  errorTecnico.add(tecnico, params.tags);
  if (r.status >= 400 && r.status < 500) {
    let codigo = String(r.status);
    try { codigo = r.json('codigo') || codigo; } catch (_) { /* cuerpo no JSON */ }
    errorNegocio.add(1, { ...params.tags, codigo });
  }
  check(r, { [`${op} 2xx`]: (x) => x.status >= 200 && x.status < 300 });
  return r;
}

const pausa = () => sleep(10 + Math.random() * 15); // think time 10–25 s (media 17.5 ≈ 18 s del requerimiento)
const celular = (n) => `9${String(n).padStart(8, '0')}`;
const azar = (lista) => lista[Math.floor(Math.random() * lista.length)];

// Mezcla de operaciones del requerimiento (suma 100).
const OPERACIONES = [
  [30, 'saldo_perfil'], [15, 'movimientos'], [15, 'transferir'], [10, 'contactos'],
  [10, 'recargar'], [6, 'consultar_deudas'], [4, 'pagar_servicio'], [10, 'otras'],
];
function elegirOperacion() {
  let x = Math.random() * 100;
  for (const [peso, op] of OPERACIONES) {
    if ((x -= peso) < 0) return op;
  }
  return 'otras';
}

const OTRAS = ['/api/limites', '/api/limites/alertas', '/api/solicitudes', '/api/seguridad/dispositivos', '/api/seguridad/sesiones'];

function operar(op, n, token) {
  const suministro = `40000${String(n).padStart(5, '0')}`; // deudas de carga de este usuario
  switch (op) {
    case 'saldo_perfil':
      llamar('GET', '/api/cuentas/me/saldo', null, token, 'saldo', 'consulta');
      llamar('GET', '/api/cuentas/me', null, token, 'perfil', 'consulta');
      break;
    case 'movimientos':
      llamar('GET', '/api/movimientos', null, token, 'movimientos', 'consulta');
      break;
    case 'transferir': // S/ 1 a otro usuario de carga: no se acerca al límite diario (S/ 2000)
      llamar('POST', '/api/transferencias',
        { tipo: 'QOLQE', celular_destino: celular((n % N_USUARIOS) + 1), monto: '1.00', descripcion: 'carga k6' },
        token, 'transferir', 'dinero');
      break;
    case 'contactos':
      llamar('GET', `/api/contactos?buscar=${azar(['a', 'e', 'o', 'carga'])}`, null, token, 'contactos', 'consulta');
      break;
    case 'recargar': // número al azar: el máximo de 5 recargas/día es por número destino
      llamar('POST', '/api/recargas', { celular: `9${Math.floor(10000000 + Math.random() * 89999999)}`, monto: 5 },
        token, 'recargar', 'dinero');
      break;
    case 'consultar_deudas':
      llamar('GET', `/api/servicios/deudas?empresa=AGUA&suministro=${suministro}`, null, token, 'consultar_deudas', 'consulta');
      break;
    case 'pagar_servicio': {
      const d = llamar('GET', `/api/servicios/deudas?empresa=AGUA&suministro=${suministro}`, null, token, 'consultar_deudas', 'consulta');
      if (d.status === 200) {
        llamar('POST', '/api/servicios/pagos', { deuda_id: d.json('0.id') }, token, 'pagar_servicio', 'dinero');
      }
      break;
    }
    default:
      llamar('GET', azar(OTRAS), null, token, 'otras', 'consulta');
  }
}

// Una iteración = una sesión: login + 6 operaciones con pausa entre cada una.
// Cada VU usa su propio usuario (900000001, 900000002, …) para que las reglas de negocio no se crucen.
export default function () {
  const n = exec.vu.idInTest;
  const login = llamar('POST', '/api/auth/login', { celular: celular(n), pin: PIN }, null, 'login', 'consulta');
  if (login.status !== 200) {
    sleep(5);
    return;
  }
  const token = login.json('access_token');
  for (let i = 0; i < 6; i++) {
    pausa();
    operar(elegirOperacion(), n, token);
  }
}
