from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine

from alembic import context

# --- ここから編集 ---
# 追加: MySQLConfigの読み込み
from infrastructure.database.config import NewMySQLConfigFromEnv
from infrastructure.database import models  # Base を import
# --- ここまで編集 ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- ここから編集 ---
# SQLAlchemy の Base.metadata を設定
target_metadata = models.Base.metadata

# 環境変数からDB接続URLを組み立てる
mysql_config = NewMySQLConfigFromEnv()
db_url = (
    f"mysql+mysqlconnector://{mysql_config.user}:{mysql_config.password}"
    f"@{mysql_config.host}:{mysql_config.port}/{mysql_config.database}"
)
config.set_main_option("sqlalchemy.url", db_url)
# --- ここまで編集 ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    # --- ここから編集 ---
    connectable = create_engine(db_url, poolclass=pool.NullPool)
    # --- ここまで編集 ---

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
