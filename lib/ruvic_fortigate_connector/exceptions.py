"""Excepciones propias del conector FortiGate.

Separan los tres tipos de fallo que el usuario debe distinguir:
autenticación, red/servidor y datos. Nunca exponemos excepciones
crípticas del cliente HTTP subyacente.
"""


class FortiGateConnectorError(Exception):
    """Error base del conector."""


class FortiGateAuthError(FortiGateConnectorError):
    """Credenciales inválidas o permisos insuficientes."""


class FortiGateNetworkError(FortiGateConnectorError):
    """No se pudo alcanzar el firewall (red/timeout)."""


class FortiGateDataError(FortiGateConnectorError):
    """La operación es válida pero el objeto/política es inválido."""
