from app import db


class SOI(db.Model):
    soi_id = db.Column(db.Integer, primary_key=True)
    soi_name = db.Column(db.String(160), unique=True)
    soi_status = db.Column(db.String(160))

    def __repr__(self):
        return f"<Product {self.soi_name}>"


class SOI_Comment(db.Model):
    soi_comment_id = db.Column(db.Integer, primary_key=True)
    what_soi_id = db.Column(db.Integer)
    soi_comment_text = db.Column(db.String(160))


class Component(db.Model):
    component_id = db.Column(db.Integer, primary_key=True)
    component_name = db.Column(db.String(160), unique=True)
    component_status = db.Column(db.String(160))

    def __repr__(self):
        return f"<Product {self.component_name}>"


class Component_Comment(db.Model):
    component_comment_id = db.Column(db.Integer, primary_key=True)
    what_component_id = db.Column(db.Integer)
    component_comment_text = db.Column(db.String(160))


class System(db.Model):
    system_id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(160), unique=True)

    def __repr__(self):
        return f"<Product {self.system_name}>"


class System_Comment(db.Model):
    system_comment_id = db.Column(db.Integer, primary_key=True)
    what_system_id = db.Column(db.Integer)
    system_comment_text = db.Column(db.String(160))
