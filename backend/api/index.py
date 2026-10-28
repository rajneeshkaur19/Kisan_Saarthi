import sys, os

# Make sure "backend/" directory root is on sys.path so "app.*" imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: F401  — Vercel picks up this `app`
