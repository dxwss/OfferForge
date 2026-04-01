"""Compatibility layer for the shared schema package.

The project started with ``schema.py`` during module 0 implementation.
This file keeps the monorepo naming convention consistent for all packages.
"""

from .schema import *  # noqa: F401,F403
