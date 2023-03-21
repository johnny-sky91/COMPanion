from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import (
    AddSystem,
    AddSOI,
    AddComponent,
    AddComponentComment,
    ChangeComponentStatus,
    ChangeSoiStatus,
)
from app.models import System, SOI, Component, ComponentComment

statuses_component = ["Status 1", "Status 2", "Status 3"]
statuses_soi = ["Status 1B", "Status 2B", "Status 3B"]


def comment_query(component_id):
    last_comment = (
        ComponentComment.query.filter_by(what_component_id=component_id)
        .order_by(ComponentComment.component_comment_id.desc())
        .first()
    )
    return last_comment


@app.route("/")
def basic_view():
    return render_template("base.html", title="Base")


@app.route("/components_list")
def components_list():
    components = Component.query.order_by(Component.component_id.asc())
    components_id = [x.component_id for x in components]
    comments_list = [
        comment_query(x).component_comment_text
        if comment_query(x) is not None
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


@app.route("/soi_list")
def soi_list():
    sois = SOI.query.order_by(SOI.soi_name.asc())
    return render_template("lists/soi_list.html", title="SOI", sois=sois)


@app.route("/soi_view/<soi_id>", methods=["GET", "POST"])
def soi_view(soi_id):
    soi = SOI.query.get(soi_id)
    return render_template("view/soi_view.html", title=f"{soi.soi_name}", soi=soi)


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


@app.route("/systems_list")
def systems_list():
    systems = System.query.order_by(System.system_name.desc())
    return render_template("lists/systems_list.html", title="Systems", systems=systems)


@app.route("/systems_list/add_new_system", methods=["GET", "POST"])
def add_new_system():
    form = AddSystem()
    if form.validate_on_submit():
        new_system = System(system_name=form.system_name.data)
        db.session.add(new_system)
        db.session.commit()
        flash(f"A new System has been added - {new_system.system_name}")
        return redirect(url_for("systems_list"))
    return render_template("add/add_new_system.html", title="Add new system", form=form)
