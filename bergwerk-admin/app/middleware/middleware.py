from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class RootPathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        prefix = request.headers.get("x-forwarded-prefix")
        if prefix:
            request.scope["root_path"] = prefix
        response = await call_next(request)
        return response