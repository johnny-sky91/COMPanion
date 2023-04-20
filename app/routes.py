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
)

statuses_component = ["Active", "No active", "EOL"]
statuses_soi = ["Active", "POE", "Not forecasted", "EOL"]
statuses_system = ["Active", "EOL"]


@app.route("/")
@app.route("/home")
def basic_view():
    soi_to_check = SOI.query.filter_by(soi_check=True).all()
    soi_last_comment = []
    for x in soi_to_check:
        try:
            soi_last_comment.append(x.soi_commentss[-1].soi_comment_text)
        except IndexError:
            soi_last_comment.append("")
    component_to_check = Component.query.filter_by(component_check=True).all()
    component_last_comment = []
    for x in component_to_check:
        try:
            component_last_comment.append(
                x.component_comments[-1].component_comment_text
            )
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


@app.route("/components_list")
def components_list():
    components = Component.query.order_by(Component.component_id.asc())
    components_id = [x.component_id for x in components]
    all_comments = [
        Component.query.filter_by(component_id=x).first().component_comments
        for x in components_id
    ]
    last_comments = [
        x[-1].component_comment_text if x else "No comment" for x in all_comments
    ]

    return render_template(
        "lists/components_list.html",
        title="Components",
        components=components,
        last_comments=last_comments,
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


@app.route("/components_list/component_view/<component_id>", methods=["GET", "POST"])
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


@app.route(
    "/components_list/component_view/<component_id>/change_check",
    methods=["GET", "POST"],
)
def component_change_check(component_id):
    component = Component.query.get(component_id)
    if component.component_check:
        component.component_check = False
    else:
        component.component_check = True
    db.session.commit()
    return redirect(request.referrer)


@app.route(
    "/components_list/component_view/<component_id>/change_status",
    methods=["GET", "POST"],
)
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


@app.route(
    "/components_list/component_view/<component_id>/add_comment",
    methods=["GET", "POST"],
)
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
    sois = SOI.query.order_by(SOI.soi_id.asc())
    sois_id = [x.soi_id for x in sois]

    all_comments = [
        SOI.query.filter_by(soi_id=x).first().soi_commentss for x in sois_id
    ]
    last_comments = [
        x[-1].soi_comment_text if x else "No comment" for x in all_comments
    ]

    def what_comp(item):
        comp = Component.query.filter_by(component_id=item).first().component_name
        return comp

    comps_joint = [
        ComponentSoi.query.join(SOI).filter_by(soi_id=soi).all() for soi in sois_id
    ]
    used_components = [
        ["No components"]
        if x == []
        else [", ".join(what_comp(item=y.what_comp_joint) for y in x)]
        for x in comps_joint
    ]

    return render_template(
        "lists/soi_list.html",
        title="SOI",
        sois=sois,
        last_comments=last_comments,
        used_components=used_components,
    )


@app.route("/soi_list/soi_view/<soi_id>", methods=["GET", "POST"])
def soi_view(soi_id):
    soi = SOI.query.get(soi_id)
    comments_list = SoiComment.query.filter_by(what_soi_id=soi_id).order_by(
        SoiComment.soi_comment_id.desc()
    )

    component_used = ComponentSoi.query.filter_by(what_soi_joint=soi_id).all()
    component_used = [
        Component.query.filter_by(component_id=x.what_comp_joint).first().component_name
        for x in component_used
    ]
    return render_template(
        "view/soi_view.html",
        title=f"{soi.soi_name}",
        soi=soi,
        comments_list=comments_list,
        component_used=component_used,
    )


@app.route("/soi_list/soi_view/<soi_id>/change_status", methods=["GET", "POST"])
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


@app.route("/soi_list/soi_view/<soi_id>/change_check", methods=["GET", "POST"])
def soi_change_check(soi_id):
    soi = SOI.query.get(soi_id)
    if soi.soi_check:
        soi.soi_check = False
    else:
        soi.soi_check = True
    db.session.commit()
    return redirect(request.referrer)


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


@app.route("/soi_list/soi_view/<soi_id>/add_comment", methods=["GET", "POST"])
def add_soi_comment(soi_id):
    soi = SOI.query.get(soi_id)
    form = AddSoiComment()
    prev = request.referrer
    print(f"1 - add comment - {prev}")
    if form.validate_on_submit():
        new_comment = SoiComment(
            what_soi_id=soi_id,
            soi_comment_text=form.soi_comment_text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment for SOI has been added")
        print(f"2 - addED comment - {prev}")
        # return redirect(prev)
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


@app.route("/systems_list/system_view/<system_id>", methods=["GET", "POST"])
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


@app.route(
    "/systems_list/system_view/<system_id>/change_check", methods=["GET", "POST"]
)
def system_change_check(system_id):
    system = System.query.get(system_id)
    if system.system_check:
        system.system_check = False
    else:
        system.system_check = True
    db.session.commit()
    return redirect(request.referrer)


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


@app.route(
    "/systems_list/system_view/<system_id>/change_status", methods=["GET", "POST"]
)
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


@app.route("/systems_list/system_view/<system_id>/add_comment", methods=["GET", "POST"])
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
@app.route("/soi_list/soi_view/<soi_id>/add_comp_soi", methods=["GET", "POST"])
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
        return redirect(url_for("soi_view", soi_id=soi_id))
    return render_template(
        "add/add_comp_soi.html", title=f"Add comp to {soi.soi_name}", form=form, soi=soi
    )
