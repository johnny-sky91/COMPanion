from app import db, models, app
from app.models import Component, Component_Comment


component_id = 1
with app.app_context():
    component = Component.query.get(component_id)
    # print(component.component_status)
    component.component_status = "Banjara Hills Secunderabad"
    db.session.commit()
