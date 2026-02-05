"""
API Routes Package
"""
from . import (
    auth,
    users,
    posts,
    payments,
    subscriptions,
    messages,
    wallet,
    notifications,
    streams,
    admin,
)

__all__ = [
    "auth",
    "users",
    "posts",
    "payments",
    "subscriptions",
    "messages",
    "wallet",
    "notifications",
    "streams",
    "admin",
]
