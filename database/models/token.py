from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.user import User


class Token(Base):
    __tablename__ = 'user_tokens'
    __table_args__ = ()

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user_account.telegram_id', ondelete='CASCADE'),
    )
    wb_token_content = mapped_column(LargeBinary, nullable=True)
    wb_token_analytic = mapped_column(LargeBinary, nullable=True)

    user: Mapped['User'] = relationship(
        'User',
        back_populates='tokens'
    )
