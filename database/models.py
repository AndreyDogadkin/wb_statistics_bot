from sqlalchemy import BigInteger, BLOB, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    """Тестовая модель для таблицы пользователя."""

    __tablename__ = 'user_account'
    __table_args__ = (
        CheckConstraint(
            'requests_per_day >= 0',
            name='requests_per_day_not_negative'
        ),
        UniqueConstraint(
            'telegram_id',
            name='telegram_id_uniq'
        )
    )

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_premium: Mapped[bool] = mapped_column(default=False)
    last_request = mapped_column(DateTime, nullable=True)
    requests_per_day: Mapped[int] = mapped_column(default=0)

    tokens: Mapped['Token'] = relationship(
        'Token',
        back_populates='user',
        cascade='all, delete',
        passive_deletes=True,
    )
    favorites: Mapped[list['FavoriteRequest']] = relationship(
        'FavoriteRequest',
        back_populates='user',
        cascade='all, delete',
        passive_deletes=True,
    )


class Token(Base):
    __tablename__ = 'user_tokens'
    __table_args__ = ()

    user_id: Mapped[int] = mapped_column(
        ForeignKey(User.telegram_id, ondelete='CASCADE'),
    )
    wb_token_content = mapped_column(BLOB, nullable=True)
    wb_token_analytic = mapped_column(BLOB, nullable=True)

    user: Mapped['User'] = relationship('User', back_populates='tokens')


class FavoriteRequest(Base):
    __tablename__ = 'user_favorites_requests'
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'nm_id', 'period',
            'all_columns_uniq'
        )
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(User.telegram_id, ondelete='CASCADE')
    )
    nm_id: Mapped[int] = mapped_column(BigInteger)
    period: Mapped[int] = mapped_column(default=1)

    user: Mapped["User"] = relationship('User', back_populates='favorites')
