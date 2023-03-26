from sqlalchemy import create_engine
from shared.settings import config

engine = create_engine(config.DB_URI, echo=config.DB_DRIVER_ECHO, future=True)


def create_tables():
    from shared.database.models import Base
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_tables()
