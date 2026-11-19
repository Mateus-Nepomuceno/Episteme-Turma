from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool, text

from turma.database import normalizar_database_url, validar_schema
from turma.models import table_registry
from turma.settings import Settings

config = context.config
_settings = Settings()
_database_url = normalizar_database_url(_settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = table_registry.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_database_url, poolclass=pool.NullPool)
    is_postgres = _database_url.startswith('postgresql')
    schema = _settings.DATABASE_SCHEMA.strip()

    with connectable.connect() as connection:
        configure_kwargs = {
            'connection': connection,
            'target_metadata': target_metadata,
        }
        if is_postgres and schema:
            schema_seguro = validar_schema(schema)
            connection.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{schema_seguro}"')
            )
            connection.execute(
                text(f'SET search_path TO "{schema_seguro}", public')
            )
            connection.commit()
            configure_kwargs['version_table_schema'] = schema_seguro

        context.configure(**configure_kwargs)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
