from app import db
from datetime import datetime


class Component(db.Model):
    __tablename__ = "component"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    description = db.Column(db.String(160))
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
    comments = db.relationship("SoiComment", backref="soi", lazy=True)
    component_joint = db.relationship("ComponentSoi", backref="soi", lazy=True)

    def __repr__(self):
        return f"<SOI {self.name}>"


class System(db.Model):
    __tablename__ = "system"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True)
    status = db.Column(db.String(160))
    check = db.Column(db.Boolean, default=False)
    comments = db.relationship("SystemComment", backref="system", lazy=True)

    def __repr__(self):
        return f"<System {self.name}>"


class ComponentComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey("component.id"))
    text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class SoiComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    soi_id = db.Column(db.Integer, db.ForeignKey("soi.id"))
    text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class SystemComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey("system.id"))
    text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class ComponentSoi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comp_joint = db.Column(db.Integer, db.ForeignKey("component.id"))
    soi_joint = db.Column(db.Integer, db.ForeignKey("soi.id"))


tables_dict = {table.__tablename__: table for table in db.Model.__subclasses__()}
