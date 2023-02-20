from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.core.db import Base


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    cover_image = Column(String(256), nullable=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="articles", uselist=False)

    def __repr__(self):
        return f"<{self.id}: {self.title}>"
