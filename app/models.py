from app import db
from datetime import datetime
from enum import Enum


class Component(db.Model):
    __tablename__ = "component"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    description = db.Column(db.String(160))
    supplier = db.Column(db.String(160))
    status = db.Column(db.String(160))
    check = db.Column(db.Boolean, default=False)
    comments = db.relationship("ComponentComment", backref="component", lazy=True)
    soi_joint = db.relationship("ComponentSoi", backref="component", lazy=True)

    def __repr__(self):
        return f"<Component {self.name}>"


class SOI(db.Model):
    __tablename__ = "soi"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    description = db.Column(db.String(160))
    status = db.Column(db.String(160))
    check = db.Column(db.Boolean, default=False)
    dummy = db.Column(db.Boolean, default=False)
    comments = db.relationship("SoiComment", backref="soi", lazy=True)
    component_joint = db.relationship("ComponentSoi", backref="soi", lazy=True)
    system_joint = db.relationship("SystemSoi", backref="soi", lazy=True)

    def __repr__(self):
        return f"<SOI {self.name}>"


class System(db.Model):
    __tablename__ = "system"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    status = db.Column(db.String(160))
    check = db.Column(db.Boolean, default=False)
    comments = db.relationship("SystemComment", backref="system", lazy=True)
    soi_joint = db.relationship("SystemSoi", backref="system", lazy=True)

    def __repr__(self):
        return f"<System {self.name}>"


class ComponentComment(db.Model):
    __tablename__ = "component_comment"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("component.id"))
    text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class SoiComment(db.Model):
    __tablename__ = "soi_comment"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("soi.id"))
    text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class SystemComment(db.Model):
    __tablename__ = "system_comment"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("system.id"))
    text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class ComponentSoi(db.Model):
    __tablename__ = "component_soi"
    id = db.Column(db.Integer, primary_key=True)
    comp_joint = db.Column(db.Integer, db.ForeignKey("component.id"))
    soi_joint = db.Column(db.Integer, db.ForeignKey("soi.id"))
    main = db.Column(db.Boolean, default=False)
    usage = db.Column(db.Integer)


class SystemSoi(db.Model):
    __tablename__ = "system_soi"
    id = db.Column(db.Integer, primary_key=True)
    system_joint = db.Column(db.Integer, db.ForeignKey("system.id"))
    soi_joint = db.Column(db.Integer, db.ForeignKey("soi.id"))


class TodoPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(160), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Enum(TodoPriority))
    deadline = db.Column(db.Date)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


tables_dict = {table.__tablename__: table for table in db.Model.__subclasses__()}
