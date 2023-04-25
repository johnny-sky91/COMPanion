from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import (
    AddComponent,
    AddSOI,
    AddSystem,
    ChangeStatus,
    AddProductComment,
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


def last_comment(table):
    table_name = tables_dict.get(table)
    product = db.session.query(table_name).order_by(table_name.id.asc())
    product_id = [x.id for x in product]
    all_comments = [
        db.session.query(table_name).filter_by(id=x).first().comments
        for x in product_id
    ]
    last_comments = [x[-1].text if x else None for x in all_comments]
    return last_comments


@app.route("/component_list")
def component_list():
    components = Component.query.order_by(Component.id.asc())
    return render_template(
        f"lists/component_list.html",
        title="Components",
        components=components,
        last_comments=last_comment(table="component"),
    )


@app.route("/system_list")
def system_list():
    systems = System.query.order_by(System.name.asc())
    return render_template(
        f"lists/system_list.html",
        title="Systems",
        systems=systems,
        last_comments=last_comment(table="system"),
    )


@app.route("/soi_list")
def soi_list():
    sois = SOI.query.order_by(SOI.id.asc())
    sois_id = [x.id for x in sois]

    def what_comp(item):
        comp = Component.query.filter_by(id=item).first().name
        return comp

    comps_joint = [
        ComponentSoi.query.join(SOI).filter_by(id=soi).all() for soi in sois_id
    ]
    used_components = [
        [""] if x == [] else [", ".join(what_comp(item=y.comp_joint) for y in x)]
        for x in comps_joint
    ]

    return render_template(
        f"lists/soi_list.html",
        title="SOI",
        sois=sois,
        last_comments=last_comment(table="soi"),
        used_components=used_components,
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


@app.route("/component_list/component_view/<id>", methods=["GET", "POST"])
def component_view(id):
    component = Component.query.get(id)
    comments_list = ComponentComment.query.filter_by(product_id=id).order_by(
        ComponentComment.id.desc()
    )
    return render_template(
        "view/component_view.html",
        title=f"{component.name}",
        component=component,
        comments_list=comments_list,
    )


@app.route("/soi_list/soi_view/<id>", methods=["GET", "POST"])
def soi_view(id):
    soi = SOI.query.get(id)
    comments_list = SoiComment.query.filter_by(product_id=id).order_by(
        SoiComment.id.desc()
    )

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


@app.route("/system_list/system_view/<id>", methods=["GET", "POST"])
def system_view(id):
    system = System.query.get(id)
    comments_list = SystemComment.query.filter_by(product_id=id).order_by(
        SystemComment.id.desc()
    )
    return render_template(
        "view/system_view.html",
        title=f"{system.name}",
        system=system,
        comments_list=comments_list,
    )


statuses_component = ["Active", "No active", "EOL"]
statuses_soi = ["Active", "POE", "Not forecasted", "EOL"]
statuses_system = ["Active", "EOL"]


@app.route("/<table>_view/<id>/change_status", methods=["GET", "POST"])
def product_change_status(table, id):
    form = ChangeStatus()
    product = db.session.query(tables_dict.get(table)).get(id)
    if table == "component":
        chosen_statuses = statuses_component
    elif table == "soi":
        chosen_statuses = statuses_soi
    else:
        chosen_statuses = statuses_system
    form.status.choices = chosen_statuses
    if form.validate_on_submit():
        product.status = form.status.data
        db.session.commit()
        return redirect(url_for(f"{table}_view", id=id))
    return render_template(
        f"update/update_{table}_status.html",
        title=f"{product.name}",
        form=form,
    )


@app.route("/<table>_view/<id>/add_comment", methods=["GET", "POST"])
def add_product_comment(table, id):
    product = db.session.query(tables_dict.get(table)).get(id)
    form = AddProductComment()
    if table == "component":
        what_comment = ComponentComment
    elif table == "soi":
        what_comment = SoiComment
    else:
        what_comment = SystemComment
    if form.validate_on_submit():
        new_comment = what_comment(
            product_id=id,
            text=form.text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash(f"New comment has been added")
        return redirect(url_for(f"{table}_view", id=id))
    return render_template(
        f"add/add_product_comment.html", title=f"{product.name}", form=form
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
