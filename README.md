# Conector Fortinet FortiGate (CON-052)

Conector Ruvic de administración para firewalls Fortinet FortiGate
(REST API v2). Permite listar políticas de firewall, agregar un objeto
de dirección, y consultar logs de tráfico recientes.

## Instalación

```bash
pip install git+https://github.com/Dgirto/FortiGate.git#subdirectory=lib
```

Python 3.10+. Dependencias: `requests>=2.31,<3.0`, `urllib3>=2.0,<3.0`.

## Permisos requeridos en FortiGate

Crea un perfil de administrador dedicado (`System → Admin Profiles`)
con acceso mínimo:

- **Read** sobre `Firewall Policy` (necesario para `list_policies`).
- **Read-Write** sobre `Firewall Address` (necesario para
  `add_address_object`).
- **Read** sobre `Log & Report` (necesario para `get_logs`).

Luego crea una cuenta de administrador de tipo **REST API Admin**
asociada a ese perfil (`System → Administrators → Create New → REST
API Admin`) y genera su token. No uses el perfil `super_admin` ni la
cuenta `admin` por defecto.

## Variables de entorno (`RUVIC_FORTIGATE_*`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `RUVIC_FORTIGATE_BASE_URL` | Sí | URL base del firewall (ej. `https://fw.empresa.com:443`) |
| `RUVIC_FORTIGATE_API_TOKEN` | Sí | Token de la cuenta REST API Admin |
| `RUVIC_FORTIGATE_VDOM` | No (default `root`) | VDOM a administrar |
| `RUVIC_FORTIGATE_VERIFY_SSL` | No (default `true`) | Verificar certificado TLS |
| `RUVIC_FORTIGATE_CONNECT_TIMEOUT` | No (default `15`) | Timeout de conexión en segundos |

## Pruebas locales

Con un FortiGate real o una FortiGate VM de evaluación (no hay imagen
Docker oficial pública; usa una instancia de laboratorio existente):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./lib

export RUVIC_FORTIGATE_BASE_URL=https://fw-lab.empresa.com:443
export RUVIC_FORTIGATE_API_TOKEN=tu-api-token
export RUVIC_FORTIGATE_VERIFY_SSL=false  # solo si el cert es autofirmado en el lab

python test_connection.py
python validate_local.py
```

Prueba también los casos de error (token inválido, VDOM inexistente,
objeto de dirección duplicado) y verifica que los mensajes sean claros.

## Notas de integración

- `list_policies` y `get_logs` son de solo lectura; `add_address_object`
  sí crea un objeto real en la configuración del firewall.
- El conector **no** modifica ni crea políticas de firewall — solo las
  consulta. Tampoco administra VPNs, rutas ni interfaces.
- Muchos FortiGate en entornos de prueba usan certificados
  autofirmados; usa `VERIFY_SSL=false` solo en esos casos, nunca en
  producción.
- Los logs se consultan desde el almacenamiento en disco del FortiGate
  (`/api/v2/monitor/log/disk/...`); si el firewall no tiene disco local
  o usa FortiAnalyzer como almacenamiento exclusivo, `get_logs` puede
  retornar resultados vacíos.
