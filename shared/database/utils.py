import functools

from sqlalchemy.inspection import inspect


@functools.lru_cache
def get_columns_name_for_do_update(model):
    """
    Поля server_default обновляем.
    """
    return [column.name for column in model.__table__.columns if not column.primary_key]


@functools.lru_cache
def get_primary_key_columns(model):
    # [column.name for column in model.__table__.primary_key.columns]
    return [column.name for column in inspect(model).primary_key]


