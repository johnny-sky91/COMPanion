from app import db
from datetime import datetime


class SOI(db.Model):
    soi_id = db.Column(db.Integer, primary_key=True)
    soi_name = db.Column(db.String(160), unique=True)
    soi_description = db.Column(db.String(160))
    soi_status = db.Column(db.String(160))
    soi_commentss = db.relationship("SoiComment", backref="soi", lazy=True)
    component_joint = db.relationship("ComponentSoi", backref="soi", lazy=True)

    def __repr__(self):
        return f"<SOI {self.soi_name}>"


class SoiComment(db.Model):
    soi_comment_id = db.Column(db.Integer, primary_key=True)
    what_soi_id = db.Column(db.Integer, db.ForeignKey("soi.soi_id"))
    soi_comment_text = db.Column(db.String(160))
    timestamp_soi_comment = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Component(db.Model):
    component_id = db.Column(db.Integer, primary_key=True)
    component_name = db.Column(db.String(160), unique=True)
    component_description = db.Column(db.String(160))
    component_status = db.Column(db.String(160))
    component_comments = db.relationship(
        "ComponentComment", backref="component", lazy=True
    )
    soi_joint = db.relationship("ComponentSoi", backref="component", lazy=True)

    def __repr__(self):
        return f"<Component {self.component_name}>"


class ComponentComment(db.Model):
    component_comment_id = db.Column(db.Integer, primary_key=True)
    what_component_id = db.Column(db.Integer, db.ForeignKey("component.component_id"))
    component_comment_text = db.Column(db.String(160))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class System(db.Model):
    system_id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(160), unique=True)
    system_status = db.Column(db.String(160))
    system_comments = db.relationship("SystemComment", backref="system", lazy=True)

    def __repr__(self):
        return f"<System {self.system_name}>"


class SystemComment(db.Model):
    system_comment_id = db.Column(db.Integer, primary_key=True)
    what_system_id = db.Column(db.Integer, db.ForeignKey("system.system_id"))
    system_comment_text = db.Column(db.String(160))
    system_comment_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )


class ComponentSoi(db.Model):
    comp_soi_id = db.Column(db.Integer, primary_key=True)
    what_comp_joint = db.Column(db.Integer, db.ForeignKey("component.component_id"))
    what_soi_joint = db.Column(db.Integer, db.ForeignKey("soi.soi_id"))
