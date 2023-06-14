import datetime
import uuid

import sqlalchemy as alchemy
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    url_photo: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    username: Mapped[str] = mapped_column(alchemy.String(length=127), nullable=False)
    register_date: Mapped[datetime.datetime] = mapped_column(alchemy.TIMESTAMP, default=datetime.datetime.utcnow)
    videos = relationship("Video",
                          back_populates="User",
                          cascade="all, delete",
                          passive_deletes=True, )

    comments = relationship("Comment",
                            back_populates="User",
                            cascade="all, delete",
                            passive_deletes=True, )


class Video(Base):
    __tablename__ = "video"
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    url_video: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    description: Mapped[str] = mapped_column(alchemy.String(2047), nullable=True)
    is_private: Mapped[bool] = mapped_column(alchemy.Boolean, default=False)
    preview: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    published_date: Mapped[datetime.datetime] = mapped_column(alchemy.TIMESTAMP, default=datetime.datetime.utcnow)
    owner_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("user.id",  ondelete="CASCADE"), nullable=False)
    comments = relationship("Comment",
                            back_populates="Video",
                            cascade="all, delete",
                            passive_deletes=True, )

class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id",  ondelete="CASCADE"), nullable=False)
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("video.id",  ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(alchemy.String(511), nullable=False)
    published_date: Mapped[datetime.datetime] = mapped_column(alchemy.TIMESTAMP, default=datetime.datetime.utcnow)
