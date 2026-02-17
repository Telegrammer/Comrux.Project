from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import StaleDataError

from application.ports.gateways import GatewayFailedError
from application.exceptions import InconsistentDataError

from .common import create_error_aware_decorator


network_error_aware = create_error_aware_decorator(
    {
        frozenset(
            {ConnectionRefusedError, ConnectionResetError, InterfaceError}
        ): GatewayFailedError
    }
)
stale_data_error_aware = create_error_aware_decorator(
    {frozenset({StaleDataError}): InconsistentDataError}
)
