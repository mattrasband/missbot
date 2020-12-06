import os


def load_secret(name):
    """load a secret first attempting the environment then falling back to
    the runtime secrets path at /run/secrets/name.lower()"""
    if (v := os.getenv(name.upper())) :
        return v

    path = f"/run/secrets/{name.lower()}"
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    raise SystemExit(f"Unable to load secret from env as {name.upper()} or /run/secrets/{name}")
