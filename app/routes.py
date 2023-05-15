from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import (
    AddComponent,
    AddSOI,
    AddSystem,
    ChangeStatus,
    AddProductComment,
    AddCompSoi,
    SearchProduct,
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
import pyperclip


@app.route("/")
@app.route("/home")
def basic_view():
    return render_template("home.html", title="Home")


def last_comment(table, products):
    table_name = tables_dict.get(table)
    product_id = [x.id for x in products]
    all_comments = [
        db.session.query(table_name).filter_by(id=x).first().comments
        for x in product_id
    ]
    last_comments = [x[-1].text if x else None for x in all_comments]
    return last_comments


@app.route("/component_list/<what_view>", methods=["GET", "POST"])
def component_list(what_view):
    form = SearchProduct()

    components = Component.query.order_by(Component.id.asc())

    if what_view.lower() == "check_true":
        components = Component.query.order_by(Component.id.asc()).filter_by(check=True)

    if form.validate_on_submit():
        components = Component.query.filter(
            (Component.name.like(f"%{form.product.data}%"))
        ).all()

    return render_template(
        f"lists/component_list.html",
        title="Components",
        form=form,
        components=components,
        last_comments=last_comment(table="component", products=components),
    )


@app.route("/get_component_list", methods=["GET", "POST"])
def get_component_list():
    components = Component.query.filter_by(status="Active").with_entities(
        Component.name
    )
    components = "\n".join([x[0] for x in components])
    pyperclip.copy(components)
    return redirect(url_for("component_list"))


@app.route("/system_list", methods=["GET", "POST"])
def system_list():
    systems = System.query.order_by(System.name.asc())
    return render_template(
        f"lists/system_list.html",
        title="Systems",
        systems=systems,
        last_comments=last_comment(table="system", products=systems),
    )


def get_used_components(products):
    def components_names(product):
        component_name = (
            Component.query.join(ComponentSoi)
            .join(SOI)
            .filter(SOI.id == product.id)
            .with_entities(Component.name)
            .all()
        )

        return ", ".join([r for (r,) in component_name])
        # return [r for (r,) in component_name]

    used_components = [components_names(product) for product in products]
    return used_components


@app.route("/soi_list/<what_view>", methods=["GET", "POST"])
def soi_list(what_view):
    form = SearchProduct()
    sois = SOI.query.order_by(SOI.id.asc())

    if what_view.lower() == "dummy_true":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(dummy=True)
    if what_view.lower() == "check_true":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(check=True)
    if what_view.lower() == "poe":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(status="POE")

    if form.validate_on_submit():
        sois = SOI.query.filter((SOI.name.like(f"%{form.product.data}%"))).all()

    last_comments = last_comment(table="soi", products=sois)
    used_components = get_used_components(products=sois)
    return render_template(
        f"lists/soi_list.html",
        title="SOI",
        sois=sois,
        last_comments=last_comments,
        used_components=used_components,
        form=form,
    )


@app.route("/component_list/add_new_component", methods=["GET", "POST"])
def add_new_component():
    form = AddComponent()
    form.status.choices = statuses_component
    if form.validate_on_submit():
        new_component = Component(
            name=form.name.data,
            description=form.description.data,
            supplier=form.supplier.data,
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
        Component.query.filter_by(id=x.comp_joint).first() for x in component_used
    ]
    return render_template(
        "view/soi_view.html",
        title=f"{soi.name}",
        soi=soi,
        comments_list=comments_list,
        component_used=component_used,
    )


@app.route(
    "/soi_list/soi_view/<id>/remove_component/<component_id>",
    methods=["GET", "POST", "DELETE"],
)
def remove_component_soi(id, component_id):
    ComponentSoi.query.filter_by(soi_joint=id, comp_joint=component_id).delete()
    db.session.commit()
    return redirect(request.referrer)


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


@app.route("/<table>_view/<id>/add_<table2>", methods=["GET", "POST"])
def add_product_comment(table, table2, id):
    product = db.session.query(tables_dict.get(table)).get(id)
    current_comment = (
        db.session.query(tables_dict.get(table))
        .filter_by(id=product.id)
        .first()
        .comments
    )[-1].text
    form = AddProductComment(text=current_comment)
    what_comment = tables_dict.get(table2)
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
        f"add/add_product_comment.html",
        title=f"{product.name}",
        form=form,
        current_comment=current_comment,
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


@app.route("/soi_view/<id>/change_dummy", methods=["GET", "POST"])
def change_dummy(id):
    to_change = db.session.query(tables_dict.get("soi")).get(id)
    if to_change.dummy:
        to_change.dummy = False
    else:
        to_change.dummy = True
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


@app.route("/other", methods=["GET", "POST"])
def other_view():
    return render_template("other.html")
