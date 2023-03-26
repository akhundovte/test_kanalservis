from sqlalchemy import (
    Column, BigInteger, Date, Numeric, DateTime
    )
from shared.database.metadata import Base
from shared.settings.config import DB_SCHEMA


class Order(Base):
    __tablename__ = 'order'

    number = Column(BigInteger, nullable=False, primary_key=True, comment='№')
    order_number = Column(BigInteger, nullable=False, comment='заказ №')
    price_usd = Column(
        Numeric(precision=10, scale=2, asdecimal=True), nullable=False, comment='стоимость,$')
    price_rur = Column(
        Numeric(precision=10, scale=2, asdecimal=True), nullable=False, comment='стоимость,руб')
    delivery_time = Column(Date, nullable=False, comment='срок поставки')
    loaded_at = Column(DateTime(timezone=True), nullable=False, index=True, comment='время загрузки')

    __table_args__ = (
        {'schema': DB_SCHEMA},
        )
