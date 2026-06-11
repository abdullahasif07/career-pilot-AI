from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def migrate_schema(engine: Engine) -> None:
    """Add new columns to existing SQLite databases (dev-friendly)."""
    if not str(engine.url).startswith("sqlite"):
        return

    inspector = inspect(engine)

    if "profiles" in inspector.get_table_names():
        existing = {col["name"] for col in inspector.get_columns("profiles")}
        profile_additions = {
            "summary": "TEXT",
            "resume_filename": "VARCHAR(512)",
            "resume_uploaded_at": "DATETIME",
        }
        with engine.begin() as conn:
            for column, col_type in profile_additions.items():
                if column not in existing:
                    conn.execute(text(f"ALTER TABLE profiles ADD COLUMN {column} {col_type}"))

    if "jobs" in inspector.get_table_names():
        existing = {col["name"] for col in inspector.get_columns("jobs")}
        job_additions = {
            "match_overall_score": "INTEGER",
            "match_strong": "JSON",
            "match_missing": "JSON",
            "match_summary": "TEXT",
            "match_computed_at": "DATETIME",
        }
        with engine.begin() as conn:
            for column, col_type in job_additions.items():
                if column not in existing:
                    conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {column} {col_type}"))
