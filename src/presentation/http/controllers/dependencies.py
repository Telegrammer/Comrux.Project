from starlette import status
from fastapi.security import HTTPBearer
from fastapi_error_map import rule
from presentation.exceptions import ServiceUnavailableTranslator, log_error, log_info

http_bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)
service_unavailable_rule = rule(
    status=status.HTTP_503_SERVICE_UNAVAILABLE,
    translator=ServiceUnavailableTranslator(),
    on_error=log_error,
)
