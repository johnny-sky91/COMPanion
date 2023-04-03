from app import db, app
from app.models import (
    Component,
    SoiComment,
    System,
    SOI,
    ComponentComment,
    SystemComment,
    ComponentSoi,
)
from sqlalchemy.orm import sessionmaker


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


list_comp = ["AAA-111-aaa", "BBB-222-bbb", "CCC-333-ccc", "DDD-444-ddd"]
list_desc = ["Comp A", "Comp B", "Comp C", "Comp D"]
list_status = ["Status 1", "Status 2", "Status 2", "Status 3"]


def comp_add_test_data(comps, desc, stat):
    with app.app_context():
        for c, d, s in zip(comps, desc, stat):
            new_component = Component(
                component_name=c,
                component_description=d,
                component_status=s,
            )
            db.session.add(new_component)
            db.session.commit()


list2_soi = [
    "SADSD-1",
    "ASDSAD-2",
    "DASDDAW-3",
    "ASDADA-4",
    "nxcnzc-5",
    "SAHDHDA-6",
    "yyyasydayd-7",
    "TTTASDTT-8",
]
list2_desc = ["SOI 1", "SOI 2", "SOI 3", "SOI 4", "SOI 5", "SOI 6", "SOI 7", "SOI 8"]
list2_status = [
    "Status 1B",
    "Status 1B",
    "Status 1B",
    "Status 1B",
    "Status 1B",
    "Status 1B",
    "Status 1B",
    "Status 1B",
]


def soi_add_test_data(sois, desc, stat):
    with app.app_context():
        for so, d, s in zip(sois, desc, stat):
            new_soi = SOI(
                soi_name=so,
                soi_description=d,
                soi_status=s,
            )
            db.session.add(new_soi)
            db.session.commit()


def clear_data():
    with app.app_context():
        db.session.query(Component).delete()
        db.session.query(ComponentComment).delete()
        db.session.query(System).delete()
        db.session.query(SystemComment).delete()
        db.session.query(SOI).delete()
        db.session.query(SoiComment).delete()
        db.session.query(ComponentSoi).delete()
        db.session.commit()


def get_list_of_comp():
    with app.app_context():
        components_list = [x.component_name for x in Component.query.all()]
        for x in components_list:
            print(x)
            print(Component.query.filter_by(component_name=x).first().component_id)


# get_list_of_comp()
# clear_data()
# soi_add_test_data(sois=list2_soi, desc=list2_desc, stat=list2_status)
# comp_add_test_data(comps=list_comp, desc=list_desc, stat=list_status)
def test_query():

    with app.app_context():
        sois = SOI.query.order_by(SOI.soi_id.asc())
        sois_id = [x.soi_id for x in sois]
        comps_joint = [
            ComponentSoi.query.join(SOI).filter_by(soi_id=soi).all() for soi in sois_id
        ]


test_query()
