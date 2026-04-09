"""
Seed runner entrypoint.

Usage (from apps/api/):
    python -m app.seeds.seed

Usage (via docker compose):
    docker compose -f infra/docker-compose.yml exec api python -m app.seeds.seed
"""

from app.database import SessionLocal
from app.seeds.demo import run


def main() -> None:
    db = SessionLocal()
    try:
        run(db)
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    main()
