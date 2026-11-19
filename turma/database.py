import re

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from turma.settings import Settings

_PADRAO_SCHEMA = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def normalizar_database_url(url: str) -> str:
    if url.startswith('postgres://'):
        return 'postgresql+psycopg://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        return 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


class SchemaInvalidoError(ValueError):
    def __init__(self, schema: str) -> None:
        super().__init__(f'Schema inválido: {schema!r}')


def validar_schema(schema: str) -> str:
    schema_limpo = schema.strip()
    if not _PADRAO_SCHEMA.fullmatch(schema_limpo):
        raise SchemaInvalidoError(schema)
    return schema_limpo


def criar_engine(database_url: str, database_schema: str = ''):
    url = normalizar_database_url(database_url)
    if url.startswith('postgresql'):
        engine_pg = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        schema = database_schema.strip()
        if schema:
            schema_seguro = validar_schema(schema)

            @event.listens_for(engine_pg, 'connect')
            def _definir_search_path(dbapi_connection, _connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute(
                    f'SET search_path TO "{schema_seguro}", public'
                )
                cursor.close()
                if not getattr(dbapi_connection, 'autocommit', True):
                    dbapi_connection.commit()

        return engine_pg
    return create_engine(url)


_settings = Settings()
engine = criar_engine(_settings.DATABASE_URL, _settings.DATABASE_SCHEMA)


def get_session():
    with Session(engine) as session:
        yield session
