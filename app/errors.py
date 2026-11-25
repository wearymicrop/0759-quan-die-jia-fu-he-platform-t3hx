from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(self, code, message, status=422):
        self.code = code
        self.message = message
        self.status = status


def render_error(_, exc):
    return JSONResponse({"code": exc.code, "message": exc.message}, status_code=exc.status)
