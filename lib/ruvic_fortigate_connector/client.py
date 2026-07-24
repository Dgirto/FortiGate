"""Cliente de administración de políticas y objetos para FortiGate (REST API).

Capacidades:
- list_policies():        listar políticas de firewall.
- add_address_object():   agregar un objeto de dirección.
- get_logs():              consultar logs de tráfico recientes.

Las credenciales SIEMPRE provienen de variables de entorno RUVIC_FORTIGATE_*
(ver config.FortiGateConfig.from_env). Prohibido hardcodearlas.
"""

from __future__ import annotations

from typing import Any

import requests
import urllib3

from .config import FortiGateConfig
from .exceptions import FortiGateAuthError, FortiGateDataError, FortiGateNetworkError
from .logging_utils import get_logger


class FortiGateClient:
    """Cliente de administración de un firewall FortiGate vía su REST API.

    Args:
        config: configuración de conexión. Si se omite, se lee de las
            variables de entorno RUVIC_FORTIGATE_* (comportamiento
            estándar en el runtime de la plataforma).

    Ejemplo:
        >>> client = FortiGateClient()  # lee RUVIC_FORTIGATE_* del entorno
        >>> client.list_policies()
        [{'policyid': 1, 'name': 'allow-web', ...}]
    """

    def __init__(self, config: FortiGateConfig | None = None) -> None:
        self.config = config or FortiGateConfig.from_env()
        self._logger = get_logger()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.config.api_token}",
                "Accept": "application/json",
            }
        )
        self._session.verify = self.config.verify_ssl
        if not self.config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.config.base_url}{path}"
        params = kwargs.pop("params", {})
        params.setdefault("vdom", self.config.vdom)
        try:
            response = self._session.request(
                method, url, params=params, timeout=self.config.connect_timeout, **kwargs
            )
        except requests.exceptions.RequestException as exc:
            raise FortiGateNetworkError(
                f"No se pudo alcanzar el firewall en {self.config.base_url!r}: {exc}"
            ) from exc

        if response.status_code in (401, 403):
            raise FortiGateAuthError(
                "Token inválido o sin permiso suficiente para esta operación/VDOM."
            )
        if response.status_code >= 400:
            raise FortiGateDataError(
                f"FortiGate respondió {response.status_code}: {response.text[:300]}"
            )
        return response

    def ping(self) -> bool:
        """Verifica la conexión consultando el estado del sistema.

        Returns:
            True si la conexión funciona.

        Raises:
            FortiGateAuthError / FortiGateNetworkError / FortiGateDataError
            según el fallo.
        """
        self._request("GET", "/api/v2/monitor/system/status")
        self._logger.info("Ping exitoso a FortiGate %s", self.config.base_url)
        return True

    # ------------------------------------------------------------------ #
    # Capacidad 1: listar políticas de firewall
    # ------------------------------------------------------------------ #

    def list_policies(self) -> list[dict[str, Any]]:
        """Lista las políticas de firewall configuradas en el VDOM.

        Returns:
            Lista de dicts, una por política.

        Ejemplo:
            >>> client.list_policies()
            [{'policyid': 1, 'name': 'allow-web', 'action': 'accept', ...}]
        """
        response = self._request("GET", "/api/v2/cmdb/firewall/policy")
        policies = response.json().get("results", [])
        self._logger.info("Se listaron %d políticas", len(policies))
        return policies

    # ------------------------------------------------------------------ #
    # Capacidad 2: agregar objeto de dirección
    # ------------------------------------------------------------------ #

    def add_address_object(
        self, name: str, subnet: str, comment: str = ""
    ) -> dict[str, Any]:
        """Agrega un objeto de dirección (address object) tipo IP/Mask.

        Args:
            name: nombre del objeto (debe ser único en el VDOM).
            subnet: subred en formato "IP MÁSCARA" (ej. "10.0.0.0 255.255.255.0")
                o "IP/CIDR" (ej. "10.0.0.0/24").
            comment: comentario opcional.

        Returns:
            Dict con la respuesta de FortiGate.

        Ejemplo:
            >>> client.add_address_object("servidor-web", "10.0.0.5/32")
            {'status': 'success', 'mkey': 'servidor-web', ...}
        """
        name = (name or "").strip()
        subnet = (subnet or "").strip()
        if not name or not subnet:
            raise FortiGateDataError("name y subnet no pueden estar vacíos.")
        if "/" in subnet:
            ip, cidr = subnet.split("/", 1)
            subnet = f"{ip} {cidr}"  # FortiOS acepta CIDR; se normaliza igual
        body = {"name": name, "type": "ipmask", "subnet": subnet, "comment": comment}
        response = self._request("POST", "/api/v2/cmdb/firewall/address", json=body)
        self._logger.info('Objeto de dirección creado: "%s" (%s)', name, subnet)
        return response.json()

    # ------------------------------------------------------------------ #
    # Capacidad 3: consultar logs recientes
    # ------------------------------------------------------------------ #

    def get_logs(self, log_type: str = "traffic", rows: int = 50) -> list[dict[str, Any]]:
        """Consulta entradas de log recientes almacenadas en disco.

        Args:
            log_type: tipo de log ("traffic", "event", "virus", "webfilter",
                "ips"). Default "traffic".
            rows: cantidad de entradas a retornar (default 50, máximo 1000).

        Returns:
            Lista de dicts, una por entrada de log.

        Ejemplo:
            >>> client.get_logs("traffic", rows=10)
            [{'srcip': '10.0.0.5', 'dstip': '8.8.8.8', 'action': 'accept', ...}]
        """
        rows = max(1, min(int(rows), 1000))
        response = self._request(
            "GET", f"/api/v2/monitor/log/disk/{log_type}", params={"rows": rows}
        )
        entries = response.json().get("results", [])
        self._logger.info('Se obtuvieron %d entradas de log "%s"', len(entries), log_type)
        return entries
