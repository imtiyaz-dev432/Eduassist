import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

REDIS_URL=os.getenv("REDIS_URL","redis://localhost:6379/0")

def get_identifier():
    """
    Returns email or mobile_no from request JSON if available; 
    falls back to client IP address.
    """
    if request.is_json:
        data=request.get_json(silent=True) or {}
        identifier=data.get("email")or data.get("mobile_no")
        if identifier:
            return str(identifier)
    return get_remote_address()

limiter=Limiter(
    key_func=get_identifier,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=REDIS_URL
)