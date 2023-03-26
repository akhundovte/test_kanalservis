import sqlalchemy as sa

from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from typing import Union, Any

from shared.database.models import Order
from shared.database.db_engine import engine
from shared.database.utils import (
    get_columns_name_for_do_update, get_primary_key_columns
    )


def save_data_by_model_with_update(
        data: Union[list, dict],
        model: Any,
):
    insert_st_q = insert(model).values(data)
    set_dict = {
        col_name: getattr(insert_st_q.excluded, col_name)
        for col_name in get_columns_name_for_do_update(model)
        }
    insert_q = insert_st_q.on_conflict_do_update(
        index_elements=get_primary_key_columns(model),
        set_=set_dict,
        )
    with engine.begin() as connection:
        connection.execute(insert_q)


def delete_orders(loaded_at: datetime):
    delete_q = sa.delete(Order) \
        .where(Order.loaded_at != loaded_at)
    with engine.begin() as connection:
        connection.execute(delete_q)
