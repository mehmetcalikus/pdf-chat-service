import time

from utils.logger import logger
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        process_time_ = time.time() - start
        logger.info(f"Response: {response.status_code}, Time: {process_time_}")
        return response
