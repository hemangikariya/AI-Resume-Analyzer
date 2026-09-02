import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Log request receipt
        logger.info(f"Incoming Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000  # in milliseconds
            
            logger.info(
                f"Completed Response: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Latency: {process_time:.2f}ms"
            )
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Failed Request: {request.method} {request.url.path} "
                f"- Error: {str(e)} - Latency: {process_time:.2f}ms"
            )
            raise e
