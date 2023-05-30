from app import app, db
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    send_file,
)
from app.forms import (
    AddComponent,
    AddSOI,
    AddSystem,
    ChangeStatus,
    AddProductComment,
    AddCompSoi,
    SearchProduct,
    AddSystemSOI,
)
from app.models import (
    System,
    SOI,
    Component,
    ComponentComment,
    SoiComment,
    SystemComment,
    ComponentSoi,
    SystemSoi,
    tables_dict,
)
import pyperclip, datetime, os
import pandas as pd


@app.route("/")
@app.route("/home")
def basic_view():
    return render_template("home.html", title="Home")


@app.route("/component_list/component_view/<id>", methods=["GET", "POST"])
def component_view(id):
    component = Component.query.get(id)
    comments = (
        ComponentComment.query.filter_by(product_id=id)
        .order_by(ComponentComment.id.desc())
        .all()
    )
    sois = SOI.query.join(ComponentSoi).filter(ComponentSoi.comp_joint == id).all()
    sois_last_comment = last_comment(table="soi", products=sois)

    return render_template(
        "view/component_view.html",
        title=f"{component.name}",
        component=component,
        comments=comments,
        sois=sois,
        sois_last_comment=sois_last_comment,
    )


@app.route("/soi_list/soi_view/<id>", methods=["GET", "POST"])
def soi_view(id):
    soi = SOI.query.get(id)
    comments = (
        SoiComment.query.filter_by(product_id=id).order_by(SoiComment.id.desc()).all()
    )
    components = (
        Component.query.join(ComponentSoi).filter(ComponentSoi.soi_joint == id).all()
    )
    components_last_comment = last_comment(table="component", products=components)
    components_details = ComponentSoi.query.filter_by(soi_joint=id).all()
    systems = System.query.join(SystemSoi).filter(SystemSoi.soi_joint == id).all()

    return render_template(
        "view/soi_view.html",
        title=f"{soi.name}",
        soi=soi,
        comments=comments,
        components=components,
        components_last_comment=components_last_comment,
        components_details=components_details,
        systems=systems,
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


@app.route("/other", methods=["GET", "POST"])
def other_view():
    return render_template("other.html")


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


@app.route("/soi_list/<what_view>", methods=["GET", "POST"])
def soi_list(what_view):
    form = SearchProduct()
    sois = SOI.query.order_by(SOI.id.asc())

    if what_view.lower() == "dummy_true":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(dummy=True)
    if what_view.lower() == "check_true":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(check=True)
    if what_view.lower() == "status_poe":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(status="POE")
    if what_view.lower() == "status_active":
        sois = SOI.query.order_by(SOI.id.asc()).filter_by(status="Active")

    if form.validate_on_submit():
        sois = SOI.query.filter((SOI.name.like(f"%{form.product.data}%"))).all()

    last_comments = last_comment(table="soi", products=sois)
    return render_template(
        f"lists/soi_list.html",
        title="SOI",
        sois=sois,
        last_comments=last_comments,
        form=form,
    )


@app.route("/system_list", methods=["GET", "POST"])
def system_list():
    systems = System.query.order_by(System.name.asc())
    return render_template(
        f"lists/system_list.html",
        title="Systems",
        systems=systems,
        last_comments=last_comment(table="system", products=systems),
    )


@app.route("/product_list_to_clipboard/<what_data>", methods=["GET", "POST"])
def product_list_to_clipboard(what_data):
    data = []
    if what_data.lower() == "active_components":
        data = Component.query.filter_by(status="Active").with_entities(Component.name)
    if what_data.lower() == "all_components":
        data = Component.query.with_entities(Component.name)
    if what_data.lower() == "all_soi_poe":
        data = SOI.query.filter_by(status="POE").with_entities(SOI.name)
    if what_data.lower() == "all_soi_active":
        data = SOI.query.filter_by(status="Active").with_entities(SOI.name)
    data = "\n".join([x[0] for x in data])
    pyperclip.copy(data)
    return redirect(request.referrer)


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

    used_components = [components_names(product) for product in products]
    return used_components


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
        return redirect(url_for("component_list", what_view="all"))
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
        return redirect(url_for("soi_list", what_view="all"))
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


def prepare_products_list(products_string):
    products = products_string.split("\n")
    products = [x.replace("\r", "") for x in products]
    products = [x for x in products if x != ""]
    return products


@app.route("/soi_list/soi_view/<id>/add_comp_soi", methods=["GET", "POST"])
def add_comp_soi(id):
    soi = SOI.query.get(id)
    form = AddCompSoi(what_soi=soi)
    if form.validate_on_submit():
        new_component_soi = ComponentSoi(
            comp_joint=Component.query.filter_by(name=form.component.data).first().id,
            soi_joint=id,
            usage=form.usage.data,
            main=form.main.data,
        )
        db.session.add(new_component_soi)
        db.session.commit()
        flash(f"New components for SOI {soi.name} has been added")
        return redirect(url_for("soi_view", id=id))
    return render_template(
        "add/add_comp_soi.html", title=f"Add comp to {soi.name}", form=form, soi=soi
    )


@app.route("/soi_list/soi_view/<id>/add_system", methods=["GET", "POST"])
def add_system_soi(id):
    soi = SOI.query.get(id)
    systems = System.query.all()
    systems = [system.name for system in systems]
    form = AddSystemSOI(what_soi=soi)
    form.system.choices = systems
    if form.validate_on_submit():
        new_system_soi = SystemSoi(
            system_joint=System.query.filter_by(name=form.system.data).first().id,
            soi_joint=id,
        )
        db.session.add(new_system_soi)
        db.session.commit()
        flash(f"{soi.name} has been added to system {form.system.data}")
        return redirect(url_for("soi_view", id=id))
    return render_template(
        "add/add_system_soi.html",
        title=f"Add system to SOI {soi.name}",
        form=form,
        soi=soi,
    )


@app.route("/<table>_view/<id>/add_<table2>", methods=["GET", "POST"])
def add_product_comment(table, table2, id):
    product = db.session.query(tables_dict.get(table)).get(id)
    current_comment = get_current_comment(table=table, product_id=product.id)
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


@app.route(
    "/soi_list/soi_view/<id>/remove_component/<component_id>",
    methods=["GET", "POST", "DELETE"],
)
def remove_component_soi(id, component_id):
    ComponentSoi.query.filter_by(soi_joint=id, comp_joint=component_id).delete()
    db.session.commit()
    return redirect(request.referrer)


@app.route(
    "/soi_list/soi_view/<id>/remove_system/<system>",
    methods=["GET", "POST", "DELETE"],
)
def remove_system_soi(id, system):
    system_id = System.query.filter_by(name=system).first().id
    SystemSoi.query.filter_by(soi_joint=id, system_joint=system_id).delete()
    db.session.commit()
    return redirect(request.referrer)


statuses_component = ["Active", "EOL"]
statuses_soi = ["Active", "POE", "EOL"]
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


def get_current_comment(table, product_id):
    try:
        current_comment = (
            db.session.query(tables_dict.get(table))
            .filter_by(id=product_id)
            .first()
            .comments
        )[-1].text
    except IndexError:
        current_comment = None
    return current_comment


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


@app.route(
    "/<table>_list/<table2>_view/<product_id>/remove_comment/<comment_id>",
    methods=["GET", "POST", "DELETE"],
)
def remove_product_comment(table, table2, product_id, comment_id):
    db.session.query(tables_dict.get(f"{table}_comment")).filter_by(
        product_id=product_id, id=comment_id
    ).delete()
    db.session.commit()
    return redirect(request.referrer)


@app.route("/other/download_data", methods=["GET", "POST"])
def download_app_data():
    soi = SOI.query.all()
    soi_table = pd.DataFrame(
        {
            "SOI": [x.name for x in soi],
            "Description": [x.description for x in soi],
            "Status": [x.status for x in soi],
            "Dummy": [x.dummy for x in soi],
            "Check": [x.check for x in soi],
            "Last_comment": last_comment(table="soi", products=soi),
        }
    )

    component = Component.query.all()
    component_table = pd.DataFrame(
        {
            "Component": [x.name for x in component],
            "Description": [x.description for x in component],
            "Status": [x.status for x in component],
            "Check": [x.check for x in component],
            "Last_comment": last_comment(table="component", products=component),
        }
    )

    now = datetime.datetime.now()
    timestamp = now.strftime("%d-%m-%H%M")
    filename = f"app_downloads/COMPanion_data_{timestamp}.xlsx"

    writer = pd.ExcelWriter(filename, engine="xlsxwriter")
    soi_table.to_excel(writer, sheet_name="SOI_info", index=False)
    component_table.to_excel(writer, sheet_name="Component_info", index=False)
    writer._save()
    path_report = os.path.join(os.getcwd(), filename)
    return send_file(path_or_file=path_report, as_attachment=True)
