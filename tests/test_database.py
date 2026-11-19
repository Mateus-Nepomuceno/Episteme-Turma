from unittest.mock import patch

import pytest

from turma.database import (
    criar_engine,
    get_session,
    normalizar_database_url,
    validar_schema,
)


def test_get_session():
    with patch('turma.database.Session'):
        session_gen = get_session()
        session = next(session_gen)
        assert session is not None


def test_normalizar_database_url():
    assert (
        normalizar_database_url('postgres://user:pass@host:5432/db')
        == 'postgresql+psycopg://user:pass@host:5432/db'
    )
    assert (
        normalizar_database_url('postgresql://user:pass@host:5432/db')
        == 'postgresql+psycopg://user:pass@host:5432/db'
    )
    assert (
        normalizar_database_url('sqlite:///database.db')
        == 'sqlite:///database.db'
    )


def test_validar_schema():
    assert validar_schema('turma') == 'turma'
    with pytest.raises(ValueError, match='Schema inválido'):
        validar_schema('1turma')


def test_criar_engine_postgres_com_schema():
    pg_engine = criar_engine(
        'postgresql://user:pass@localhost:5432/db', 'turma'
    )
    assert pg_engine.dialect.name == 'postgresql'
    assert pg_engine.pool._pre_ping is True
    pg_engine.dispose()
