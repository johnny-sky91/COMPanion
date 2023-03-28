from app import db, models, app
from app.models import Component, ComponentComment, SystemComment


def comment_query(component_id):
    last_comment = (
        ComponentComment.query.filter_by(what_component_id=component_id)
        .order_by(ComponentComment.component_comment_id.desc())
        .first()
    )
    return last_comment


def test_for_query():
    with app.app_context():
        components = Component.query.order_by(Component.component_id.asc())
        components_id = [x.component_id for x in components]
        comments_list = [
            comment_query(x).component_comment_text
            if comment_query(x) is not None
            else "None"
            for x in components_id
        ]
    return comments_list
