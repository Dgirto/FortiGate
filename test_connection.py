"""Prueba de conexión estándar del conector fortigate.

Firma estándar Ruvic: def test_connection() -> tuple[bool, str]
- Lee la configuración EXCLUSIVAMENTE de las env vars RUVIC_FORTIGATE_*.
- Nunca lanza excepciones; retorna (ok, mensaje).

Ejecutable también como script para pruebas locales:
    python test_connection.py
"""

from __future__ import annotations


def test_connection() -> tuple[bool, str]:
    """Conecta al FortiGate y consulta el estado del sistema usando las
    env vars RUVIC_FORTIGATE_*."""
    try:
        from ruvic_fortigate_connector import (
            FortiGateAuthError,
            FortiGateClient,
            FortiGateDataError,
            FortiGateNetworkError,
        )
    except ImportError:
        return (
            False,
            "La librería ruvic-fortigate-connector no está instalada. "
            "Instala con: pip install git+https://github.com/Dgirto/"
            "FortiGate.git#subdirectory=lib",
        )

    try:
        client = FortiGateClient()  # valida que existan las env vars
    except ValueError as exc:
        return False, str(exc)

    try:
        client.ping()
    except FortiGateAuthError as exc:
        return False, f"Autenticación fallida: {exc}"
    except FortiGateNetworkError as exc:
        return False, f"Error de red: {exc}"
    except FortiGateDataError as exc:
        return False, f"Error de datos: {exc}"
    except Exception as exc:  # red de seguridad: jamás propagar
        return False, f"Error inesperado: {exc}"

    return (
        True,
        f"Conexión exitosa a FortiGate ({client.config.base_url})",
    )


if __name__ == "__main__":
    ok, message = test_connection()
    print(f"{'OK' if ok else 'FALLO'}: {message}")
    raise SystemExit(0 if ok else 1)
