import datetime
from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Text,
    Date,
    ForeignKey
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    password = Column(String, nullable=False)

Index('user_name_idx', User.name, unique=True)


class Language(Base):
    __tablename__ = 'lanuages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

Index('lanuage_name_idx', Language.name, unique=True)


class Catalog(Base):
    __tablename__ = 'catalogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    language_id = Column(Integer, ForeignKey(Language.id))
    user_id = Column(Integer, ForeignKey(User.id))
    name = Column(String, unique=True)
    date = Column(Date, default=datetime.date.today())
    # relationship: each catalog belongs to one language
    language = relationship(Language)

Index('catalog_name_idx', Catalog.name, unique=True)


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True, autoincrement=True)
    catalog_id = Column(Integer, ForeignKey(Catalog.id))
    name = Column(String, unique=True)
    pronunciation = Column(String)
    value = Column(Text)
    date = Column(Date, default=datetime.date.today()) # default value is today
    # relationship
    catalog = relationship(Catalog)

Index('word_name_idx', Word.name, unique=True)
