from datetime import datetime
import json, operator

from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
import pandas as pd

from app import db
from flask import current_app as app
from app.forms import (
    AddComponent,
    AddSOI,
    AddSystem,
    ChangeStatus,
    AddProductComment,
    AddCompSoi,
    SearchProduct,
    AddSystemSOI,
    AddGroup,
    AddGroupProduct,
    AddProductNote,
)
from app.models import (
    tables_dict,
    System,
    SOI,
    Component,
    ComponentComment,
    SoiComment,
    SystemComment,
    ComponentSoi,
    SystemSoi,
    MyGroup,
    MyGroupProduct,
    MyGroupComment,
)


@app.context_processor
def inject_date_cw():
    current_date = datetime.now().date()
    week_number = current_date.isocalendar()[1]
    return dict(current_date=current_date, week_number=week_number)


@app.route("/my_group_list/my_group_view/<id>/change_content", methods=["GET", "POST"])
def change_group_content(id):
    group = MyGroup.query.get(id)
    group_products = MyGroupProduct.query.filter_by(my_group_id=id).all()
    sois = [SOI.query.filter_by(id=pair.soi_id).first() for pair in group_products]
    components = [
        Component.query.filter_by(id=pair.component_id).first()
        for pair in group_products
    ]
    data = zip(sois, components, group_products)
    return render_template(
        "update/update_group.html",
        title=f"{group.name}_change_content",
        group=group,
        group_products=group_products,
        data=data,
    )


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
    sois_names = json.dumps([soi.name for soi in sois])
    what_group = MyGroupProduct.query.filter_by(component_id=id).first()
    if what_group is None:
        group = None
    else:
        group = MyGroup.query.filter_by(id=what_group.my_group_id).first()
    return render_template(
        "view/component_view.html",
        title=f"{component.name}",
        component=component,
        comments=comments,
        sois=sois,
        sois_names=sois_names,
        sois_last_comment=sois_last_comment,
        group=group,
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
    components_names = json.dumps([component.name for component in components])
    what_group = MyGroupProduct.query.filter_by(soi_id=id).first()
    if what_group is None:
        group = None
    else:
        group = MyGroup.query.filter_by(id=what_group.my_group_id).first()
    return render_template(
        "view/soi_view.html",
        title=f"{soi.name}",
        soi=soi,
        comments=comments,
        components=components,
        components_names=components_names,
        components_last_comment=components_last_comment,
        components_details=components_details,
        systems=systems,
        group=group,
    )


def group_pivot(soi_ids, comp_ids):
    soi = [SOI.query.get(soi_id) for soi_id in soi_ids]
    comp_usage = [
        ComponentSoi.query.filter_by(soi_joint=x).first().usage for x in soi_ids
    ]
    component = [Component.query.get(component_id) for component_id in comp_ids]
    data = {
        "SOI": soi,
        "Component": component,
        "Usage": comp_usage,
    }
    group_df = pd.DataFrame(data)
    group_pivot = group_df.pivot_table(
        index=["SOI"],
        columns=["Component"],
        values="Usage",
        aggfunc="first",
        fill_value=0,
        sort=False,
    )

    results_soi = group_pivot.index.tolist()
    results_component = group_pivot.columns.tolist()
    results_usage = group_pivot.values.tolist()
    soi_usage = zip(results_soi, results_usage)
    return results_component, soi_usage


@app.route("/my_group_list/my_group_view/<id>", methods=["GET", "POST"])
def my_group_view(id):
    group = MyGroup.query.get(id)
    group_products = MyGroupProduct.query.filter_by(my_group_id=id).all()
    for x in group_products:
        print(x)
    soi_ids = [product.soi_id for product in group_products]
    comp_ids = [product.component_id for product in group_products]

    data_group = group_pivot(soi_ids=soi_ids, comp_ids=comp_ids)

    sois = [SOI.query.get(soi_id) for soi_id in soi_ids]
    sois_names = json.dumps(list(set([soi.name for soi in sois])))

    components = [Component.query.get(component_id) for component_id in comp_ids]
    components_names = json.dumps(
        list(set([component.name for component in components]))
    )

    comments = (
        MyGroupComment.query.filter_by(product_id=id)
        .order_by(MyGroupComment.id.desc())
        .all()
    )

    systems = set()
    for soi_id in set(soi_ids):
        one_soi_systems = (
            System.query.join(SystemSoi).filter(SystemSoi.soi_joint == soi_id).all()
        )
        systems.update(one_soi_systems)

    systems = sorted(list(systems), key=operator.attrgetter("name"))
    return render_template(
        "view/my_group_view.html",
        title=f"{group.name}",
        group=group,
        components=data_group[0],
        soi_usage=data_group[1],
        comments=comments,
        sois_names=sois_names,
        components_names=components_names,
        systems=systems,
    )


@app.route("/my_group_list/next_group/<step>/<int:id>", methods=["GET"])
def next_group(step, id):
    if step.lower() == "forward":
        new_id = id + 1
    else:
        new_id = id - 1

    next_group = MyGroup.query.get(new_id)
    if next_group:
        return redirect(url_for("my_group_view", id=new_id))
    else:
        flash("No more groups")
        return redirect(url_for("my_group_view", id=id))


@app.route("/system_list/system_view/<id>", methods=["GET", "POST"])
def system_view(id):
    system = System.query.get(id)
    sois = SOI.query.join(SystemSoi).filter(SystemSoi.system_joint == id).all()
    comments = (
        SystemComment.query.filter_by(product_id=id)
        .order_by(SystemComment.id.desc())
        .all()
    )
    return render_template(
        "view/system_view.html",
        title=f"{system.name}",
        system=system,
        comments=comments,
        sois=sois,
    )


def last_comment(table, products):
    table_name = tables_dict.get(table)
    product_id = [x.id for x in products]
    all_comments = [
        db.session.query(table_name).filter_by(id=x).first().comments
        for x in product_id
    ]
    last_comments = [x[-1] if x else None for x in all_comments]
    return last_comments


def groups_list(products):
    groups_list = []
    for product in products:
        if not product.my_group:
            groups_list.append(None)
        else:
            group_id = product.my_group[0].my_group_id
            group = MyGroup.query.get(group_id)
            groups_list.append(group if group else None)
    return groups_list


@app.route("/component_list/<what_view>", methods=["GET", "POST"])
def component_list(what_view):
    query_mapping = {
        "check_true": {"check": True},
        "active_components": {"status": "Active"},
        "eol_components": {"status": "EOL"},
    }
    components_query = Component.query

    if what_view.lower() in query_mapping:
        query_filters = query_mapping[what_view.lower()]
        components_query = components_query.filter_by(**query_filters)

    form_search = SearchProduct()

    if form_search.submit_search.data and form_search.validate():
        to_search = form_search.product.data
        components_query = components_query.filter(
            Component.name.like(f"%{to_search}%")
            | Component.codenumber.like(f"%{to_search}%")
        )

    components = components_query.order_by(Component.id.asc()).all()

    components_names = json.dumps([component.name for component in components])
    components_codnumbers = json.dumps(
        [component.codenumber for component in components]
    )

    groups = groups_list(products=components)
    last_comments = last_comment(table="component", products=components)

    return render_template(
        "lists/component_list.html",
        title="Components",
        form_search=form_search,
        components_names=components_names,
        components_codnumbers=components_codnumbers,
        components=components,
        groups=groups,
        last_comments=last_comments,
    )


@app.route("/soi_list/<what_view>", methods=["GET", "POST"])
def soi_list(what_view):
    sois = SOI.query.order_by(SOI.id.asc())
    query_mapping = {
        "dummy_true": {"dummy": True},
        "check_true": {"check": True},
        "status_active_forecasted": {"status": "Active - forecasted"},
        "status_poe": {"status": "Active - POE"},
        "status_active_not_forecasted": {"status": "Active - not forecasted"},
        "status_eol": {"status": "Not active - EOL"},
    }

    if what_view.lower() in query_mapping:
        query_filters = query_mapping[what_view.lower()]
        sois = sois.filter_by(**query_filters)

    elif what_view.lower() == "status_active_forecasted_and_poe":
        sois = sois.filter(SOI.status.in_(["Active - POE", "Active - forecasted"]))

    form_search = SearchProduct()
    if form_search.validate_on_submit():
        sois = SOI.query.filter((SOI.name.like(f"%{form_search.product.data}%"))).all()

    sois_names = json.dumps([soi.name for soi in sois])
    last_comments = last_comment(table="soi", products=sois)
    groups = groups_list(products=sois)

    return render_template(
        f"lists/soi_list.html",
        title="SOI",
        sois=sois,
        sois_names=sois_names,
        last_comments=last_comments,
        form_search=form_search,
        groups=groups,
    )


@app.route("/my_group_list/<what_view>", methods=["GET", "POST"])
def my_group_list(what_view):
    groups = MyGroup.query.order_by(MyGroup.id.asc())

    query_mapping = {
        "check_true": {"check": True},
        "status_active": {"status": "Active"},
        "status_eol": {"status": "EOL"},
        "status_nmb": {"status": "NMB"},
    }
    if what_view.lower() in query_mapping:
        query_filters = query_mapping[what_view.lower()]
        groups = groups.filter_by(**query_filters)
    last_comments = last_comment(table="my_group", products=groups)
    return render_template(
        f"lists/my_group_list.html",
        title="Groups",
        last_comments=last_comments,
        groups=groups,
    )


@app.route("/system_list/<what_view>", methods=["GET", "POST"])
def system_list(what_view):
    systems = System.query.order_by(System.name.asc())

    query_mapping = {
        "check_true": {"check": True},
        "status_active": {"status": "Active"},
        "status_eol": {"status": "EOL"},
        "status_nmb": {"status": "NMB"},
    }
    if what_view.lower() in query_mapping:
        query_filters = query_mapping[what_view.lower()]
        systems = systems.filter_by(**query_filters)

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
        flash(f"New component added - {new_component.name}")
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
        flash(f"New SOI added - {new_soi.name}")
        return redirect(url_for("soi_list", what_view="all"))
    return render_template("add/add_new_soi.html", title="Add new SOI", form=form)


@app.route("/my_group_list/add_new_group", methods=["GET", "POST"])
def add_new_group():
    groups = MyGroup.query.all()
    form = AddGroup()
    if not groups:
        if request.method == "POST" and form.validate_on_submit():
            new_group_name = f"{form.name.data}_01"
            new_group = MyGroup(name=new_group_name)
            db.session.add(new_group)
            db.session.commit()

            flash(f"New group added - {new_group.name}")
            return redirect(url_for("my_group_list"))

        return render_template(
            "add/add_new_group.html", title="Add new group", form=form
        )
    else:
        last_group = groups[-1]
        last_group_name, last_group_no = last_group.name.split("_")
        new_group_no = str(int(last_group_no) + 1).zfill(len(last_group_no))
        new_group_name = f"{last_group_name}_{new_group_no}"

        new_group = MyGroup(name=new_group_name)
        db.session.add(new_group)
        db.session.commit()

        flash(f"New group added - {new_group.name}")
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
        flash(f"New system added - {new_system.name}")
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
        flash(f"New components for SOI {soi.name} added")
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
        flash(f"{soi.name} added to system {form.system.data}")
        return redirect(url_for("soi_view", id=id))
    return render_template(
        "add/add_system_soi.html",
        title=f"Add system to SOI {soi.name}",
        form=form,
        soi=soi,
    )


@app.route("/my_group_list/my_group_view/<id>/add_product", methods=["GET", "POST"])
def add_my_group_product(id):
    group = MyGroup.query.get(id)
    form = AddGroupProduct()
    if form.validate_on_submit():
        new_soi = SOI.query.filter_by(name=form.soi.data).first()
        new_comp = Component.query.filter_by(name=form.component.data).first()
        new_product_group = MyGroupProduct(
            my_group_id=id, soi_id=new_soi.id, component_id=new_comp.id
        )
        db.session.add(new_product_group)
        db.session.commit()
        flash(
            f"SOI {new_soi.name} and component {new_comp.name} added to group {group.name}"
        )
        return redirect(url_for("my_group_view", id=id))
    return render_template(
        "add/add_group_product.html",
        title=f"Add product to group {group.name}",
        form=form,
        group=group,
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
        flash(f"New comment added")
        return redirect(url_for(f"{table}_view", id=id))
    return render_template(
        f"add/add_product_comment.html",
        title=f"{product.name}",
        form=form,
        current_comment=current_comment,
    )


@app.route("/<table>_view/<id>/add_note", methods=["GET", "POST"])
def add_new_note(table, id):
    product = db.session.query(tables_dict.get(table)).get(id)
    form = AddProductNote()
    if form.validate_on_submit():
        product.note = form.note.data
        db.session.commit()
        return redirect(url_for(f"{table}_view", id=id))
    return render_template(
        f"add/add_new_note.html",
        title=f"{product.name}",
        form=form,
        current_note=product.note,
        product=product,
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


@app.route(
    "/my_group_list/my_group_view/<id>/remove_product/<pair_id>",
    methods=["GET", "POST", "DELETE"],
)
def remove_my_group_product(id, pair_id):
    group = MyGroup.query.get(id)
    pair = MyGroupProduct.query.filter_by(id=pair_id)
    soi = SOI.query.filter_by(id=pair.first().soi_id).first()
    component = Component.query.filter_by(id=pair.first().component_id).first()
    pair.delete()
    db.session.commit()
    flash(
        f"SOI {soi.name} and component {component.name} removed from group {group.name}"
    )
    return redirect(request.referrer)


statuses_component = ["Active", "EOL", "NMB"]
statuses_soi = [
    "Active - forecasted",
    "Active - not forecasted",
    "Active - POE",
    "Not active - EOL",
    "NMB",
]
statuses_system = ["Active", "EOL", "NMB"]


@app.route("/<table>_view/<id>/change_status", methods=["GET", "POST"])
def product_change_status(table, id):
    form = ChangeStatus()

    tables_dict = {
        "component": Component,
        "soi": SOI,
        "system": System,
        "my_group": MyGroup,
    }

    chosen_statuses = {
        "component": statuses_component,
        "soi": statuses_soi,
        "system": statuses_system,
        "my_group": statuses_system,
    }
    product = db.session.query(tables_dict.get(table)).get(id)

    form.status.choices = chosen_statuses.get(table, [])

    if form.validate_on_submit():
        product.status = form.status.data
        db.session.commit()
        return redirect(url_for(f"{table}_view", id=id))
    return render_template(
        f"update/update_status.html",
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
    to_change.check = not to_change.check
    db.session.commit()
    return redirect(request.referrer)


@app.route("/soi_view/<id>/change_dummy", methods=["GET", "POST"])
def change_dummy(id):
    to_change = db.session.query(tables_dict.get("soi")).get(id)
    to_change.dummy = not to_change.dummy
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
