from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
import traceback

class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Capture error details and print traceback
            tb = traceback.format_exc()
            logger.error(f"Unhandled Exception occurred for {request.method} {request.url.path}: {exc}\nTraceback:\n{tb}")
            
            # Format according to API spec requirements
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred. Please try again later."
                    }
                }
            )
