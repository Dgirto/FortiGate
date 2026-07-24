"""Conector Ruvic de administración de políticas y objetos para FortiGate."""

from .client import FortiGateClient
from .config import ENV_PREFIX, FortiGateConfig
from .exceptions import (
    FortiGateAuthError,
    FortiGateConnectorError,
    FortiGateDataError,
    FortiGateNetworkError,
)
from .logging_utils import setup_logging

__all__ = [
    "ENV_PREFIX",
    "FortiGateAuthError",
    "FortiGateClient",
    "FortiGateConfig",
    "FortiGateConnectorError",
    "FortiGateDataError",
    "FortiGateNetworkError",
    "setup_logging",
]

__version__ = "1.0.0"
