"""Alembic environment configuration for FairCheck.

Dynamically resolves the database path from the FairCheck db module
so migrations always target the correct local SQLite file.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ---------------------------------------------------------------------------
# Ensure the project root is importable so ``faircheck`` resolves.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from faircheck.api.db import DB_DIR, Base  # noqa: E402
from faircheck.api import models  # noqa: E402, F401  — registers ORM tables

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to .ini values.
# ---------------------------------------------------------------------------
config = context.config

# Override the static sqlalchemy.url with the dynamic FairCheck path.
config.set_main_option("sqlalchemy.url", f"sqlite:///{DB_DIR}/sessions.db")

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic's autogenerate at our ORM metadata.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL — no Engine required.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
