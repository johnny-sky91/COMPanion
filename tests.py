from app import db, models, app
from app.models import Component, Component_Comment


with app.app_context():
    components = Component.query.order_by(Component.component_id.asc())
    for component in components:
        print(component.component_comments[0].component_comment_text)
