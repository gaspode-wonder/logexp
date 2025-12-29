from . import bp_health


@bp_health.get("/health")
def health():
    return {"status": "ok"}
