#!/usr/bin/env python3
"""Load a small set of synthetic demo tasks into the local database.

All data is fictional and for local demo use only. Existing rows are left
in place; pass --reset to drop and recreate the tasks table first.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Base, SessionLocal, engine, get_database_url  # noqa: E402
from app.models import Task  # noqa: E402

SYNTHETIC_TASKS = [
    {
        "title": "Write the API README",
        "description": "Document local setup and example requests.",
        "priority": "high",
        "completed": False,
    },
    {
        "title": "Add pagination tests",
        "description": "Cover skip/limit and equal-timestamp ordering.",
        "priority": "high",
        "completed": True,
    },
    {
        "title": "Sketch OpenAPI examples",
        "description": "Keep request bodies short and realistic.",
        "priority": "medium",
        "completed": False,
    },
    {
        "title": "Tidy project structure",
        "description": None,
        "priority": "low",
        "completed": False,
    },
    {
        "title": "Review error responses",
        "description": "Confirm 404 and 422 bodies stay consistent.",
        "priority": "medium",
        "completed": False,
    },
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed synthetic demo tasks.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate the tasks table before seeding.",
    )
    args = parser.parse_args(argv)

    print(f"Database: {get_database_url()}")
    if args.reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(Task).count()
        if existing and not args.reset:
            print(
                f"Found {existing} existing task(s); leaving them unchanged. "
                "Re-run with --reset to replace with synthetic demo data."
            )
            return 0
        for item in SYNTHETIC_TASKS:
            db.add(Task(**item))
        db.commit()
        print(f"Inserted {len(SYNTHETIC_TASKS)} synthetic tasks.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
