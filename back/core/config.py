from dataclasses import dataclass
import os
from urllib.parse import quote_plus


@dataclass(frozen=True)
class Settings:
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    projector_name: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "workout_tracker"),
            postgres_user=os.getenv("POSTGRES_USER", "postgres"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            projector_name=os.getenv("PROJECTOR_NAME", "workout_tracker_projector"),
        )

    @property
    def postgres_dsn(self) -> str:
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql://{user}:{password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def eventsourcing_env(self) -> dict[str, str]:
        return {
            "PERSISTENCE_MODULE": "eventsourcing.postgres",
            "POSTGRES_DBNAME": self.postgres_db,
            "POSTGRES_HOST": self.postgres_host,
            "POSTGRES_PORT": str(self.postgres_port),
            "POSTGRES_USER": self.postgres_user,
            "POSTGRES_PASSWORD": self.postgres_password,
            "CREATE_TABLE": "yes",
            "IS_SNAPSHOTTING_ENABLED": "y",
        }
