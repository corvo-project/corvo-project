from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from .database import Base

toponym_variant_pages = Table(
    "toponym_variant_pages",
    Base.metadata,
    Column("toponym_variant_id", Integer, ForeignKey("toponym_variants.id"), primary_key=True),
    Column("page_id", Integer, ForeignKey("pages.id"), primary_key=True),
)

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
    toponym_variants = relationship("ToponymVariant", secondary=toponym_variant_pages, back_populates="pages")

class Toponym(Base):
    __tablename__ = "toponyms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location_info = Column(String)

    variants = relationship("ToponymVariant", back_populates="toponym")

class ToponymVariant(Base):
    __tablename__ = "toponym_variants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    toponym_id = Column(Integer, ForeignKey("toponyms.id"), nullable=False)

    toponym = relationship("Toponym", back_populates="variants")
    pages = relationship("Page", secondary=toponym_variant_pages, back_populates="toponym_variants")

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
