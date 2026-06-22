from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    file_name = Column(String)
    total_pages = Column(Integer)
    pages = relationship("Page", back_populates="document")

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    page_number = Column(Integer, index=True)
    text_content = Column(Text)

    document = relationship("Document", back_populates="pages")
    events = relationship("Event", back_populates="page")

class EventDescription(Base):
    __tablename__ = "event_descriptions"

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)

    events = relationship("Event", back_populates="event_description")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    offset = Column(Integer, nullable=False)
    term = Column(String, nullable=False)
    event_type = Column(Integer, ForeignKey("event_descriptions.id"), nullable=False)
    sentence = Column(String, nullable=False)

    page = relationship("Page", back_populates="events")
    event_description = relationship("EventDescription", back_populates="events")
