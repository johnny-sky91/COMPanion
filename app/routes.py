from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import (
    AddSystem,
    AddSOI,
    AddComponent,
    AddComponentComment,
    ChangeComponentStatus,
    ChangeSoiStatus,
    AddSoiComment,
    ChangeSystemStatus,
    AddSystemComment,
    AddCompSoi,
)
from app.models import (
    System,
    SOI,
    Component,
    ComponentComment,
    SoiComment,
    SystemComment,
    ComponentSoi,
    tables_dict,
)

statuses_component = ["Active", "No active", "EOL"]
statuses_soi = ["Active", "POE", "Not forecasted", "EOL"]
statuses_system = ["Active", "EOL"]


@app.route("/")
@app.route("/home")
def basic_view():
    soi_to_check = SOI.query.filter_by(check=True).all()
    soi_last_comment = []
    for x in soi_to_check:
        try:
            soi_last_comment.append(x.comments[-1].text)
        except IndexError:
            soi_last_comment.append("")
    component_to_check = Component.query.filter_by(check=True).all()
    component_last_comment = []
    for x in component_to_check:
        try:
            component_last_comment.append(x.comments[-1].text)
        except IndexError:
            component_last_comment.append("")
    return render_template(
        "home.html",
        title="Home",
        sois=soi_to_check,
        components=component_to_check,
        sois_comment=soi_last_comment,
        components_comment=component_last_comment,
    )


@app.route("/component_list")
def component_list():
    components = Component.query.order_by(Component.id.asc())
    components_id = [x.id for x in components]
    all_comments = [
        Component.query.filter_by(id=x).first().comments for x in components_id
    ]
    last_comments = [x[-1].text if x else "No comment" for x in all_comments]

    return render_template(
        "lists/component_list.html",
        title="Components",
        components=components,
        last_comments=last_comments,
    )


@app.route("/component_list/add_new_component", methods=["GET", "POST"])
def add_new_component():
    form = AddComponent()
    form.status.choices = statuses_component
    if form.validate_on_submit():
        new_component = Component(
            name=form.name.data,
            description=form.description.data,
            status=form.status.data,
        )
        db.session.add(new_component)
        db.session.commit()
        flash(f"A new component has been added - {new_component.name}")
        return redirect(url_for("component_list"))
    return render_template(
        "add/add_new_component.html", title="Add new Component", form=form
    )


@app.route("/component_list/component_view/<id>", methods=["GET", "POST"])
def component_view(id):
    component = Component.query.get(id)
    comments_list = ComponentComment.query.filter_by(component_id=id).order_by(
        ComponentComment.id.desc()
    )
    return render_template(
        "view/component_view.html",
        title=f"{component.name}",
        component=component,
        comments_list=comments_list,
    )


@app.route(
    "/component_list/component_view/<id>/change_status",
    methods=["GET", "POST"],
)
def component_change_status(id):
    form = ChangeComponentStatus()
    component = Component.query.get(id)
    form.status.choices = statuses_component
    if form.validate_on_submit():
        component.status = form.status.data
        db.session.commit()
        return redirect(url_for("component_view", id=id))
    return render_template(
        "update/update_component_status.html",
        title=f"{component.name}",
        form=form,
    )


@app.route(
    "/component_list/component_view/<id>/add_comment",
    methods=["GET", "POST"],
)
def add_component_comment(id):
    component = Component.query.get(id)
    form = AddComponentComment()
    if form.validate_on_submit():
        new_comment = ComponentComment(
            component_id=id,
            text=form.text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for component has been added")
        return redirect(url_for("component_view", id=id))
    return render_template(
        "add/add_component_comment.html", title=f"{component.name}", form=form
    )


@app.route("/soi_list")
def soi_list():
    sois = SOI.query.order_by(SOI.id.asc())
    sois_id = [x.id for x in sois]

    all_comments = [SOI.query.filter_by(id=x).first().comments for x in sois_id]
    last_comments = [x[-1].text if x else "No comment" for x in all_comments]

    def what_comp(item):
        comp = Component.query.filter_by(id=item).first().name
        return comp

    comps_joint = [
        ComponentSoi.query.join(SOI).filter_by(id=soi).all() for soi in sois_id
    ]
    used_components = [
        ["No components"]
        if x == []
        else [", ".join(what_comp(item=y.comp_joint) for y in x)]
        for x in comps_joint
    ]

    return render_template(
        "lists/soi_list.html",
        title="SOI",
        sois=sois,
        last_comments=last_comments,
        used_components=used_components,
    )


@app.route("/soi_list/soi_view/<id>", methods=["GET", "POST"])
def soi_view(id):
    soi = SOI.query.get(id)
    comments_list = SoiComment.query.filter_by(soi_id=id).order_by(SoiComment.id.desc())

    component_used = ComponentSoi.query.filter_by(soi_joint=id).all()
    component_used = [
        Component.query.filter_by(id=x.comp_joint).first().name for x in component_used
    ]
    return render_template(
        "view/soi_view.html",
        title=f"{soi.name}",
        soi=soi,
        comments_list=comments_list,
        component_used=component_used,
    )


@app.route("/soi_list/soi_view/<id>/change_status", methods=["GET", "POST"])
def soi_change_status(id):
    form = ChangeSoiStatus()
    soi = SOI.query.get(id)
    form.status.choices = statuses_soi

    if form.validate_on_submit():
        soi.status = form.status.data
        db.session.commit()
        return redirect(url_for("soi_view", id=id))
    return render_template(
        "update/update_soi_status.html",
        title=f"{soi.name}",
        form=form,
    )


@app.route("/soi_list/add_new_soi", methods=["GET", "POST"])
def add_new_soi():
    form = AddSOI()
    form.status.choices = statuses_soi
    if form.validate_on_submit():
        new_soi = SOI(
            name=form.name.data,
            description=form.description.data,
            status=form.status.data,
        )
        db.session.add(new_soi)
        db.session.commit()
        flash(f"A new SOI has been added - {new_soi.name}")
        return redirect(url_for("soi_list"))
    return render_template("add/add_new_soi.html", title="Add new SOI", form=form)


@app.route("/soi_list/soi_view/<id>/add_comment", methods=["GET", "POST"])
def add_soi_comment(id):
    soi = SOI.query.get(id)
    form = AddSoiComment()
    prev = request.referrer
    print(f"1 - add comment - {prev}")
    if form.validate_on_submit():
        new_comment = SoiComment(
            soi_id=id,
            text=form.text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for SOI has been added")
        print(f"2 - addED comment - {prev}")
        # return redirect(prev)
        return redirect(url_for("soi_view", id=soi.id))
    return render_template("add/add_soi_comment.html", title=f"{soi.name}", form=form)


def system_comment_query(id):
    last_comment = (
        SystemComment.query.filter_by(system_id=id)
        .order_by(SystemComment.id.desc())
        .first()
    )
    return last_comment


@app.route("/system_list")
def system_list():
    systems = System.query.order_by(System.name.asc())
    id = [x.id for x in systems]
    comments_list = [
        system_comment_query(x).text
        if system_comment_query(x) is not None
        else "No comment"
        for x in id
    ]

    return render_template(
        "lists/system_list.html",
        title="Systems",
        systems=systems,
        comments_list=comments_list,
    )


@app.route("/system_list/system_view/<id>", methods=["GET", "POST"])
def system_view(id):
    system = System.query.get(id)
    comments_list = SystemComment.query.filter_by(system_id=id).order_by(
        SystemComment.id.desc()
    )
    return render_template(
        "view/system_view.html",
        title=f"{system.name}",
        system=system,
        comments_list=comments_list,
    )


@app.route("/<table_name>_view/<id>/change_check", methods=["GET", "POST"])
def change_check(table_name, id):
    to_change = db.session.query(tables_dict.get(table_name)).get(id)
    if to_change.check:
        to_change.check = False
    else:
        to_change.check = True
    db.session.commit()
    return redirect(request.referrer)


@app.route("/system_list/add_new_system", methods=["GET", "POST"])
def add_new_system():
    form = AddSystem()
    form.status.choices = statuses_system
    if form.validate_on_submit():
        new_system = System(
            name=form.name.data,
            status=form.status.data,
        )
        db.session.add(new_system)
        db.session.commit()
        flash(f"A new System has been added - {new_system.name}")
        return redirect(url_for("system_list"))
    return render_template("add/add_new_system.html", title="Add new system", form=form)


@app.route("/system_list/system_view/<id>/change_status", methods=["GET", "POST"])
def system_change_status(id):
    form = ChangeSystemStatus()
    system = System.query.get(id)
    form.status.choices = statuses_system
    if form.validate_on_submit():
        system.status = form.status.data
        db.session.commit()
        return redirect(url_for("system_view", id=id))
    return render_template(
        "update/update_system_status.html",
        title=f"{system.name}",
        form=form,
    )


@app.route("/system_list/system_view/<id>/add_comment", methods=["GET", "POST"])
def add_system_comment(id):
    system = System.query.get(id)
    form = AddSystemComment()
    if form.validate_on_submit():
        new_comment = SystemComment(
            system_id=id,
            text=form.text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for system has been added")
        return redirect(url_for("system_view", id=system.id))
    return render_template(
        "add/add_system_comment.html", title=f"{system.name}", form=form
    )


# TODO
@app.route("/soi_list/soi_view/<id>/add_comp_soi", methods=["GET", "POST"])
def add_comp_soi(id):
    soi = SOI.query.get(id)
    form = AddCompSoi()
    form.component.choices = [x.name for x in Component.query.all()]
    if form.validate_on_submit():
        new_joint = ComponentSoi(
            comp_joint=Component.query.filter_by(name=form.component.data).first().id,
            soi_joint=id,
        )
        db.session.add(new_joint)
        db.session.commit()
        flash(f"New component for SOI {soi.name} has been added")
        return redirect(url_for("soi_view", id=id))
    return render_template(
        "add/add_comp_soi.html", title=f"Add comp to {soi.name}", form=form, soi=soi
    )
