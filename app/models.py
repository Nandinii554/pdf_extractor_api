from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    total_pages = Column(Integer)
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete")

class DocumentPage(Base):
    __tablename__ = "document_page"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id"))
    page_number = Column(Integer)
    width = Column(Float)
    height = Column(Float)

    document = relationship("Document", back_populates="pages")
    lines = relationship("Line", back_populates="page", cascade="all, delete")
    words = relationship("Word", back_populates="page", cascade="all, delete")
    tables = relationship("Table", back_populates="page", cascade="all, delete")

class Line(Base):
    __tablename__ = "line"
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("document_page.id"))
    line_number = Column(Integer)
    text = Column(Text)
    bbox_x0 = Column(Float)
    bbox_y0 = Column(Float)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)

    page = relationship("DocumentPage", back_populates="lines")

class Word(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("document_page.id"))
    word_index = Column(Integer)
    text = Column(String(255))
    bbox_x0 = Column(Float)
    bbox_y0 = Column(Float)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)

    page = relationship("DocumentPage", back_populates="words")

class Table(Base):
    __tablename__ = "table"
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("document_page.id"))
    bbox_x0 = Column(Float)
    bbox_y0 = Column(Float)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)

    page = relationship("DocumentPage", back_populates="tables")
    cells = relationship("TableCell", back_populates="table", cascade="all, delete")

class TableCell(Base):
    __tablename__ = "table_cell"
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey("table.id"))
    row = Column(Integer)
    col = Column(Integer)
    text = Column(Text)
    bbox_x0 = Column(Float)
    bbox_y0 = Column(Float)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)
    is_header = Column(Integer, default=0)  

    table = relationship("Table", back_populates="cells")
