from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy import BigInteger, Integer, String, Text, DateTime, ForeignKey, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram 64-bit user_id
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    files: Mapped[List["UploadedFile"]] = relationship(
        "UploadedFile", back_populates="user", cascade="all, delete-orphan"
    )

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="files")

async def cleanup_old_records(session: AsyncSession, hours: int = 24) -> int:
    """
    Видаляє записи з БД (UploadedFile), старіші за вказану кількість годин (за замовчуванням 24 години).
    Повертає кількість видалених записів.
    """
    threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    stmt = delete(UploadedFile).where(UploadedFile.created_at < threshold)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount or 0
