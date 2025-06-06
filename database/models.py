from datetime import datetime
from typing import Optional

from sqlalchemy import(
    String, Integer, ForeignKey, DateTime, func, BigInteger, Text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(1024), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    subscribed_to_channel: Mapped[bool] = mapped_column(default=False, nullable=False)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    usages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Generation(Base):
    __tablename__ = 'generations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, success, error
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    public_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    liked: Mapped[bool] = mapped_column(default=False, nullable=False)


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_rub: Mapped[int] = mapped_column(Integer, nullable=False)
    generations_count: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmed: Mapped[bool] = mapped_column(default=False, nullable=False)
    payment_provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'donatepay', 'boosty', и т.д.
    external_id: Mapped[str] = mapped_column(String(255), nullable=True)  # ID из сторонней системы
