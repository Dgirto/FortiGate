---
name: fortigate
description: >
  Usa la librería ruvic_fortigate_connector para administrar un firewall
  Fortinet FortiGate - listar políticas de firewall (list_policies),
  agregar un objeto de dirección (add_address_object), y consultar logs
  de tráfico recientes (get_logs). Úsala cuando el usuario pida revisar
  reglas de firewall, agregar una IP/subred permitida, o consultar
  tráfico registrado en FortiGate.
triggers:
- fortigate
- fortinet
- firewall
- política de firewall
---

# Conector FortiGate (ruvic_fortigate_connector)

Librería Python de administración para Fortinet FortiGate. Está **preinstalada en el runtime** cuando el conector está configurado (si no, instálala con `pip install git+https://github.com/Dgirto/FortiGate.git#subdirectory=lib`).

## Regla crítica de credenciales

El código generado **NUNCA hardcodea credenciales**. Siempre se leen de variables de entorno, disponibles cuando el conector `fortigate` está configurado:

| Variable | Contenido |
|----------|-----------|
| `RUVIC_FORTIGATE_BASE_URL` | URL base del firewall |
| `RUVIC_FORTIGATE_API_TOKEN` | Token de la cuenta REST API Admin |
| `RUVIC_FORTIGATE_VDOM` | (opcional) VDOM, default `root` |
| `RUVIC_FORTIGATE_VERIFY_SSL` | (opcional) `true`/`false`, default `true` |
| `RUVIC_FORTIGATE_CONNECT_TIMEOUT` | (opcional) timeout en segundos |

Si estas variables NO existen, el conector no está configurado: no generes código que lo use; indica al usuario que lo configure en **Settings → Conectores**.

## Este conector escribe (solo objetos de dirección)

`add_address_object` crea un objeto real en la configuración del firewall. `list_policies` y `get_logs` son de solo lectura. El conector NO modifica políticas ni reglas existentes.

## Conexión (siempre igual)

```python
from ruvic_fortigate_connector import FortiGateClient

client = FortiGateClient()  # lee RUVIC_FORTIGATE_* del entorno automáticamente
```

## Capacidad 1 — Listar políticas de firewall

```python
policies = client.list_policies()
for p in policies:
    print(f"{p['policyid']}: {p['name']} ({p['action']})")
```

## Capacidad 2 — Agregar un objeto de dirección

```python
client.add_address_object("servidor-web", "10.0.0.5/32", comment="Servidor web interno")
```

`subnet` acepta formato CIDR (`10.0.0.0/24`) o "IP MÁSCARA" (`10.0.0.0 255.255.255.0`).

## Capacidad 3 — Consultar logs de tráfico

```python
logs = client.get_logs("traffic", rows=20)
for entry in logs:
    print(f"{entry.get('srcip')} -> {entry.get('dstip')} ({entry.get('action')})")
```

Tipos de log soportados: `traffic`, `event`, `virus`, `webfilter`, `ips`.

## Manejo de errores

```python
from ruvic_fortigate_connector import (
    FortiGateAuthError, FortiGateDataError, FortiGateNetworkError,
)

try:
    policies = client.list_policies()
except FortiGateAuthError:
    print("Token inválido o sin permiso suficiente")
except FortiGateNetworkError:
    print("No se pudo alcanzar el firewall — reintenta en unos segundos")
except FortiGateDataError as e:
    print(f"Error de datos: {e}")
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de las variables `RUVIC_FORTIGATE_*` (el constructor de `FortiGateClient` ya lo hace).
2. Nunca imprimas `RUVIC_FORTIGATE_API_TOKEN` en logs ni en la salida.
3. `add_address_object` modifica configuración real del firewall: confirma con el usuario antes de crear un objeto si no fue pedido explícitamente.
4. El conector NO crea ni modifica políticas de firewall — solo las consulta. Si el usuario pide crear/modificar una política, indícale que esta capacidad no está disponible.
5. Usa `rows` razonable en `get_logs` (default 50, máximo 1000) para no traer volúmenes de log excesivos.
