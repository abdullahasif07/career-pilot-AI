from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def migrate_schema(engine: Engine) -> None:
    """Add new columns to existing SQLite databases (dev-friendly)."""
    if not str(engine.url).startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "profiles" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("profiles")}
    additions = {
        "summary": "TEXT",
        "resume_filename": "VARCHAR(512)",
        "resume_uploaded_at": "DATETIME",
    }

    with engine.begin() as conn:
        for column, col_type in additions.items():
            if column not in existing:
                conn.execute(text(f"ALTER TABLE profiles ADD COLUMN {column} {col_type}"))
