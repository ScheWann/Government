from datetime import datetime
from almanac_backend import db

aso_idx_tbl = db.Table('aso_idx_tbl',
    db.Column('idx_id', db.Integer, db.ForeignKey('t_index.id'), primary_key=True),
    db.Column('tbl_id', db.Integer, db.ForeignKey('t_table.id'), primary_key=True)
)

aso_rgn_usr = db.Table('aso_rgn_usr',
    db.Column('rgn_id', db.Integer, db.ForeignKey('t_region.id'), primary_key=True),
    db.Column('usr_id', db.String(32), db.ForeignKey('t_user.id'), primary_key=True)
)

class Index(db.Model):
    __tablename__ = 't_index'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    tables = db.relationship('Table', secondary=aso_idx_tbl, back_populates='indexes')

    def __init__(self, name):
        self.name = name

class Table(db.Model):
    __tablename__ = 't_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    region_id = db.Column(db.Integer, db.ForeignKey('t_region.id'))
    region = db.relationship('Region', back_populates='tables')

    indexes = db.relationship('Index', secondary=aso_idx_tbl, back_populates='tables')
    datas = db.relationship('Dataset', back_populates='table', cascade="all, delete, delete-orphan")

    def __init__(self, name):
        self.name = name

class Region(db.Model):
    __tablename__ = 't_region'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(6))
    create_at = db.Column(db.DateTime)

    tables = db.relationship('Table', back_populates='region', cascade="all, delete, delete-orphan")
    users = db.relationship('User', secondary=aso_rgn_usr, back_populates='regions')
    bundle = db.relationship('Bundle', back_populates='region', cascade="all, delete, delete-orphan")

    def __init__(self, name):
        self.name = name
        self.create_at = datetime.utcnow()

class Bundle(db.Model):
    __tablename__ = 't_bundle'

    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.Integer)
    pie = db.Column(db.Integer)
    column = db.Column(db.Integer)
    radar = db.Column(db.Integer)

    region_id = db.Column(db.Integer, db.ForeignKey('t_region.id'))
    region = db.relationship('Region', back_populates='bundle')

    def __init__(self, line, pie, column, radar, region):
        self.column = column
        self.line = line
        self.pie = pie
        self.radar = radar
        self.region = region

class Dataset(db.Model):
    __tablename__ = 't_data'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Numeric(precision=14, scale=5))

    row_index_id = db.Column(db.Integer, db.ForeignKey('t_index.id'))
    row_index = db.relationship('Index', foreign_keys='Dataset.row_index_id')
    col_index_id = db.Column(db.Integer, db.ForeignKey('t_index.id'))
    col_index = db.relationship('Index', foreign_keys='Dataset.col_index_id')

    table_id = db.Column(db.Integer, db.ForeignKey('t_table.id'))
    table = db.relationship('Table', back_populates='datas')

    def __init__(self, data):
        self.data = data

from flask_login import UserMixin
import uuid
class User(db.Model, UserMixin):
    __tablename__ = 't_user'

    id = db.Column(db.String(32), default=uuid.uuid1().hex, primary_key=True)
    username = db.Column(db.String(11), unique=True)
    password = db.Column(db.String(60))
    level = db.Column(db.Integer, default=0)

    regions = db.relationship('Region', secondary=aso_rgn_usr, back_populates='users')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Msg(db.Model):
    __tablename__ = 't_msg'

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer)
    user_id = db.Column(db.String(32))
    msg = db.Column(db.String(200))
    state = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime)

    def __init__(self, rid, uid, msg):
        self.region_id = rid
        self.user_id = uid
        self.msg = msg
        self.create_at = datetime.utcnow()
