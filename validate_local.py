"""Validación local del conector fortigate: ejercita las 3 capacidades.

Uso:
    python validate_local.py

Requiere las variables RUVIC_FORTIGATE_* exportadas en el entorno, con
un token de una cuenta REST API Admin con los permisos del README.
"""

from ruvic_fortigate_connector import FortiGateClient, setup_logging

setup_logging("INFO")
client = FortiGateClient()

print("== 1. Listar políticas de firewall ==")
policies = client.list_policies()
for p in policies[:5]:
    print(f"  {p.get('policyid')}: {p.get('name')} ({p.get('action')})")

print("== 2. Agregar objeto de dirección ==")
result = client.add_address_object("ruvic-test-host", "203.0.113.10/32", comment="Prueba Ruvic")
print(f"  {result.get('status')}")

print("== 3. Consultar logs de tráfico ==")
logs = client.get_logs("traffic", rows=10)
print(f"  {len(logs)} entradas")

print("\nTodo OK: list_policies, add_address_object y get_logs funcionan.")
