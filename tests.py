from app import db, models, app
from app.models import Component, Component_Comment


component_id = 4
with app.app_context():
    component = Component.query.get(component_id)
    comments_list = Component_Comment.query.filter_by(
        what_component_id=component_id
    ).order_by(Component_Comment.component_comment_id.desc())

    for x in comments_list:
        print(x.component_comment_text)
