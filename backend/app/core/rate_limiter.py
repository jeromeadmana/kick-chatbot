# app/core/rate_limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings

# For demo: in-memory storage. In production set up Redis via limits storage config.
limiter = Limiter(key_func=get_remote_address)
