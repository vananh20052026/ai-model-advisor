from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Document(Base):
    """Uploaded documents (PDF, CSV)."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    source_type = Column(String(50))
    file_size = Column(Integer)
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    chats = relationship("ChatHistory", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_documents_filename", "filename"),)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename})>"


class ChatHistory(Base):
    """Chat conversations with retrieved context."""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    retrieved_chunks = Column(JSONB)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chats")

    __table_args__ = (Index("idx_chat_created_at", "created_at"),)

    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, question={self.question[:30]}...)>"