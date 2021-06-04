from typing import Tuple

from sqlalchemy import TIMESTAMP, Column, func


def get_common_columns() -> Tuple[Column]:
    return (
        Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", TIMESTAMP(timezone=True), nullable=True)
    )
