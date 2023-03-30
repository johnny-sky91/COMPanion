from app import app, db
from flask import render_template, flash, redirect, url_for
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
)

statuses_component = ["Status 1", "Status 2", "Status 3"]
statuses_soi = ["Status 1B", "Status 2B", "Status 3B"]
statuses_system = ["Status 1C", "Status 2C", "Status 3C"]


@app.route("/")
def basic_view():
    return render_template("base.html", title="Base")


def component_comment_query(component_id):
    last_comment = (
        ComponentComment.query.filter_by(what_component_id=component_id)
        .order_by(ComponentComment.component_comment_id.desc())
        .first()
    )
    return last_comment


@app.route("/components_list")
def components_list():
    components = Component.query.order_by(Component.component_id.asc())
    components_id = [x.component_id for x in components]
    comments_list = [
        component_comment_query(x).component_comment_text
        if component_comment_query(x) is not None
        else "No comment"
        for x in components_id
    ]
    return render_template(
        "lists/components_list.html",
        title="Components",
        components=components,
        comments_list=comments_list,
    )


@app.route("/components_list/add_new_component", methods=["GET", "POST"])
def add_new_component():
    form = AddComponent()
    form.component_status.choices = statuses_component
    if form.validate_on_submit():
        new_component = Component(
            component_name=form.component_name.data,
            component_description=form.component_description.data,
            component_status=form.component_status.data,
        )
        db.session.add(new_component)
        db.session.commit()
        flash(f"A new component has been added - {new_component.component_name}")
        return redirect(url_for("components_list"))
    return render_template(
        "add/add_new_component.html", title="Add new Component", form=form
    )


@app.route("/component_view/<component_id>", methods=["GET", "POST"])
def component_view(component_id):
    component = Component.query.get(component_id)
    comments_list = ComponentComment.query.filter_by(
        what_component_id=component_id
    ).order_by(ComponentComment.component_comment_id.desc())
    return render_template(
        "view/component_view.html",
        title=f"{component.component_name}",
        component=component,
        comments_list=comments_list,
    )


@app.route("/component_view/<component_id>/change_status", methods=["GET", "POST"])
def component_change_status(component_id):
    form = ChangeComponentStatus()
    component = Component.query.get(component_id)
    form.component_status.choices = statuses_component
    if form.validate_on_submit():
        component.component_status = form.component_status.data
        db.session.commit()
        return redirect(url_for("component_view", component_id=component_id))
    return render_template(
        "update/update_component_status.html",
        title=f"{component.component_name}",
        form=form,
    )


@app.route("/component_view/<component_id>/add_comment", methods=["GET", "POST"])
def add_component_comment(component_id):
    component = Component.query.get(component_id)
    form = AddComponentComment()
    if form.validate_on_submit():
        new_comment = ComponentComment(
            what_component_id=component_id,
            component_comment_text=form.component_comment_text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for component has been added")
        return redirect(url_for("component_view", component_id=component_id))
    return render_template(
        "add/add_component_comment.html", title=f"{component.component_name}", form=form
    )


def soi_comment_query(soi_id):
    last_comment = (
        SoiComment.query.filter_by(what_soi_id=soi_id)
        .order_by(SoiComment.soi_comment_id.desc())
        .first()
    )
    return last_comment


@app.route("/soi_list")
def soi_list():
    sois = SOI.query.order_by(SOI.soi_id.asc())
    soi_id = [x.soi_id for x in sois]
    comments_list = [
        soi_comment_query(x).soi_comment_text
        if soi_comment_query(x) is not None
        else "No comment"
        for x in soi_id
    ]

    return render_template(
        "lists/soi_list.html", title="SOI", sois=sois, comments_list=comments_list
    )


@app.route("/soi_view/<soi_id>", methods=["GET", "POST"])
def soi_view(soi_id):
    soi = SOI.query.get(soi_id)
    comments_list = SoiComment.query.filter_by(what_soi_id=soi_id).order_by(
        SoiComment.soi_comment_id.desc()
    )
    return render_template(
        "view/soi_view.html",
        title=f"{soi.soi_name}",
        soi=soi,
        comments_list=comments_list,
    )


@app.route("/soi_view/<soi_id>/change_status", methods=["GET", "POST"])
def soi_change_status(soi_id):
    form = ChangeSoiStatus()
    soi = SOI.query.get(soi_id)
    form.soi_status.choices = statuses_soi
    if form.validate_on_submit():
        soi.soi_status = form.soi_status.data
        db.session.commit()
        return redirect(url_for("soi_view", soi_id=soi_id))
    return render_template(
        "update/update_soi_status.html",
        title=f"{soi.soi_name}",
        form=form,
    )


@app.route("/soi_list/add_new_soi", methods=["GET", "POST"])
def add_new_soi():
    form = AddSOI()
    form.soi_status.choices = statuses_soi
    if form.validate_on_submit():
        new_soi = SOI(
            soi_name=form.soi_name.data,
            soi_description=form.soi_description.data,
            soi_status=form.soi_status.data,
        )
        db.session.add(new_soi)
        db.session.commit()
        flash(f"A new SOI has been added - {new_soi.soi_name}")
        return redirect(url_for("soi_list"))
    return render_template("add/add_new_soi.html", title="Add new SOI", form=form)


@app.route("/soi_view/<soi_id>/add_comment", methods=["GET", "POST"])
def add_soi_comment(soi_id):
    soi = SOI.query.get(soi_id)
    form = AddSoiComment()
    if form.validate_on_submit():
        new_comment = SoiComment(
            what_soi_id=soi_id,
            soi_comment_text=form.soi_comment_text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for SOI has been added")
        return redirect(url_for("soi_view", soi_id=soi.soi_id))
    return render_template(
        "add/add_soi_comment.html", title=f"{soi.soi_name}", form=form
    )


def system_comment_query(system_id):
    last_comment = (
        SystemComment.query.filter_by(what_system_id=system_id)
        .order_by(SystemComment.system_comment_id.desc())
        .first()
    )
    return last_comment


@app.route("/systems_list")
def systems_list():
    systems = System.query.order_by(System.system_name.asc())
    system_id = [x.system_id for x in systems]
    comments_list = [
        system_comment_query(x).system_comment_text
        if system_comment_query(x) is not None
        else "No comment"
        for x in system_id
    ]

    return render_template(
        "lists/systems_list.html",
        title="Systems",
        systems=systems,
        comments_list=comments_list,
    )


@app.route("/system_view/<system_id>", methods=["GET", "POST"])
def system_view(system_id):
    system = System.query.get(system_id)
    comments_list = SystemComment.query.filter_by(what_system_id=system_id).order_by(
        SystemComment.system_comment_id.desc()
    )
    return render_template(
        "view/system_view.html",
        title=f"{system.system_name}",
        system=system,
        comments_list=comments_list,
    )


@app.route("/systems_list/add_new_system", methods=["GET", "POST"])
def add_new_system():
    form = AddSystem()
    form.system_status.choices = statuses_system
    if form.validate_on_submit():
        new_system = System(
            system_name=form.system_name.data,
            system_status=form.system_status.data,
        )
        db.session.add(new_system)
        db.session.commit()
        flash(f"A new System has been added - {new_system.system_name}")
        return redirect(url_for("systems_list"))
    return render_template("add/add_new_system.html", title="Add new system", form=form)


@app.route("/system_view/<system_id>/change_status", methods=["GET", "POST"])
def system_change_status(system_id):
    form = ChangeSystemStatus()
    system = System.query.get(system_id)
    form.system_status.choices = statuses_system
    if form.validate_on_submit():
        system.system_status = form.system_status.data
        db.session.commit()
        return redirect(url_for("system_view", system_id=system_id))
    return render_template(
        "update/update_system_status.html",
        title=f"{system.system_name}",
        form=form,
    )


@app.route("/system_view/<system_id>/add_comment", methods=["GET", "POST"])
def add_system_comment(system_id):
    system = System.query.get(system_id)
    form = AddSystemComment()
    if form.validate_on_submit():
        new_comment = SystemComment(
            what_system_id=system_id,
            system_comment_text=form.system_comment_text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for system has been added")
        return redirect(url_for("system_view", system_id=system.system_id))
    return render_template(
        "add/add_system_comment.html", title=f"{system.system_name}", form=form
    )


# TODO
@app.route("/soi_view/<soi_id>/add_comp_soi", methods=["GET", "POST"])
def add_comp_soi(soi_id):
    soi = SOI.query.get(soi_id)
    form = AddCompSoi()
    form.what_component.choices = [x.component_name for x in Component.query.all()]
    if form.validate_on_submit():
        new_joint = ComponentSoi(
            what_comp_joint=Component.query.filter_by(
                component_name=form.what_component.data
            )
            .first()
            .component_id,
            what_soi_joint=soi_id,
        )
        db.session.add(new_joint)
        db.session.commit()
        flash(f"New component for SOI {soi.soi_name} has been added")
        for x in ComponentSoi.query.all():
            print(x.what_comp_joint, x.what_soi_joint)
        return redirect(url_for("soi_view", soi_id=soi_id))
    return render_template(
        "add/add_comp_soi.html", title=f"Add comp to {soi.soi_name}", form=form, soi=soi
    )
