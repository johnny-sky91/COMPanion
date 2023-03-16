from app import db, models, app
from app.models import Component, Component_Comment


component_id = 1
with app.app_context():
    components = Component.query.order_by(Component.component_id.asc())
    for x in components:
        print("Name - ", x.component_name)
        comments = Component_Comment.query.filter_by(what_component_id=x.component_id)
        for y in comments:
            print(y.component_comment_text)
