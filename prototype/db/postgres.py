from contextlib import contextmanager
from typing import Iterator

from psycopg import Connection, connect
from psycopg.rows import dict_row


class PostgresConnectionFactory:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        with connect(self._dsn, row_factory=dict_row) as conn:
            yield conn
