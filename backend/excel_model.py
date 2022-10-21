import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine
ng = create_engine('mysql://root:3Zsqlpas5*@localhost/opengovf', echo=False)
from sqlalchemy.orm import sessionmaker, scoped_session
ss_fac = sessionmaker(bind=ng)
Session = scoped_session(ss_fac)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, String, Numeric, DateTime
from sqlalchemy import Table as STable
from sqlalchemy.orm import relationship
aso_idx_tbl = STable('aso_idx_tbl', Base.metadata,
    Column('idx_id', Integer, ForeignKey('t_index.id')),
    Column('tbl_id', Integer, ForeignKey('t_table.id'))
)
class Index(Base):
    __tablename__ = 't_index'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), unique=True)

    tables = relationship('Table', secondary=aso_idx_tbl, back_populates='indexes')

    def __init__(self, name):
        self.name = name

class Table(Base):
    __tablename__ = 't_table'

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    region_id = Column(Integer, ForeignKey('t_region.id'))
    region = relationship('Region', back_populates='tables')

    indexes = relationship('Index', secondary=aso_idx_tbl, back_populates='tables')
    datas = relationship('Dataset', back_populates='table', cascade="all, delete, delete-orphan")

    def __init__(self, name):
        self.name = name

class Region(Base):
    __tablename__ = 't_region'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=6), unique=True)
    state = Column(Integer, default=0)
    create_at = Column(DateTime, default=datetime.utcnow())

    tables = relationship('Table', back_populates='region', cascade="all, delete, delete-orphan")

    def __init__(self, name):
        self.name = name

class Dataset(Base):
    __tablename__ = 't_data'

    id = Column(Integer, primary_key=True)
    data = Column(Numeric(precision=14, scale=5))

    row_index_id = Column(Integer, ForeignKey('t_index.id'))
    row_index = relationship('Index', foreign_keys='Dataset.row_index_id')
    col_index_id = Column(Integer, ForeignKey('t_index.id'))
    col_index = relationship('Index', foreign_keys='Dataset.col_index_id')

    table_id = Column(Integer, ForeignKey('t_table.id'))
    table = relationship('Table', back_populates='datas')

    def __init__(self, data):
        self.data = data

from flask_login import UserMixin
import uuid
class Admin(Base, UserMixin):
    __tablename__ = 't_admin'

    id = Column(String(length=32), default=uuid.uuid1().hex, primary_key=True)
    username = Column(String(length=11), unique=True)
    password = Column(String(length=60))

    def __init__(self, username, password):
        self.username = username
        self.password = password