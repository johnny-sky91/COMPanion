import io
from datetime import datetime

import pandas as pd
from flask import redirect, request, render_template, flash, make_response

from app import db
from app.routes import last_comment
from app.others import others
from app.forms import AddGroupsFile
from app.models import (
    System,
    SOI,
    Component,
    ComponentSoi,
    SystemSoi,
    MyGroup,
    MyGroupProduct,
    tables_dict,
)


@others.route("/other", methods=["GET", "POST"])
def other_view():
    groups_form = AddGroupsFile()
    if groups_form.validate_on_submit():
        file = groups_form.groups_file.data
        data = pd.read_excel(file)
        print(data)
        flash(f"Groups updated!")
        return redirect(request.referrer)
    return render_template("other.html", title="Other", groups_form=groups_form)


@others.route("/other/download_data", methods=["GET", "POST"])
def download_app_data():
    soi = SOI.query.all()
    component = Component.query.all()
    group = MyGroup.query.all()
    system = System.query.all()
    system_soi = SystemSoi.query.all()
    bom = ComponentSoi.query.all()

    soi_table = create_soi_table(soi)
    component_table = create_component_table(component)
    group_table = create_group_table(group)
    system_tabel = create_system_table(system)
    system_soi_table = create_system_soi_table(system_soi)
    bom_tabel = create_bom_table(bom)

    now = datetime.now()
    timestamp = now.strftime("%d%m%y_%H%M")
    filename = f"COMPanion_data_{timestamp}"

    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine="xlsxwriter")

    soi_table.to_excel(excel_writer=writer, index=False, sheet_name="SOI_info")
    component_table.to_excel(
        excel_writer=writer, index=False, sheet_name="Component_info"
    )
    group_table.to_excel(excel_writer=writer, index=False, sheet_name="Group_info")
    system_tabel.to_excel(excel_writer=writer, index=False, sheet_name="System_info")
    system_soi_table.to_excel(excel_writer=writer, index=False, sheet_name="System_SOI")
    bom_tabel.to_excel(excel_writer=writer, index=False, sheet_name="BOM")

    writer._save()

    download_response = make_response(out.getvalue())

    download_response.headers["Content-Disposition"] = (
        f"attachment; filename={filename}.xlsx"
    )
    download_response.headers["Content-type"] = "application/x-xlsx"

    return download_response


@others.route("/other/download_groups_update_file", methods=["GET", "POST"])
def download_groups_update_file():
    update_table = pd.DataFrame(columns=["SOI", "COMPONENT", "GROUP"])

    now = datetime.now()
    timestamp = now.strftime("%d%m%y_%H%M")
    filename = f"COMPanion_groups_update_{timestamp}"

    out = io.BytesIO()

    writer = pd.ExcelWriter(out, engine="xlsxwriter")
    update_table.to_excel(excel_writer=writer, index=False, sheet_name="Groups_update")
    writer._save()

    download_response = make_response(out.getvalue())
    download_response.headers["Content-Disposition"] = (
        f"attachment; filename={filename}.xlsx"
    )
    download_response.headers["Content-type"] = "application/x-xlsx"

    return download_response


@others.route("/other/upload_groups_update_file", methods=["GET", "POST"])
def upload_groups_update_file():
    form = AddGroupsFile()
    if form.validate_on_submit():
        groups_file = form.groups_file.data
        if groups_file and groups_file.filename.endswith(".xlsx"):
            data = pd.read_excel(io.BytesIO(groups_file.read()))
            msg = groups_mass_change(group_data=data)
            flash(msg)
            return redirect(request.referrer)
        else:
            flash("Please upload a valid Excel file (.xlsx)")
    return redirect(request.referrer)


def groups_mass_change(group_data):
    MyGroupProduct.query.delete()
    db.session.commit()
    if set(group_data.columns) != set(["SOI", "COMPONENT", "GROUP"]):
        return f"Wrong file uploaded!"
    for index, row in group_data.iterrows():
        soi = SOI.query.filter_by(name=row["SOI"]).first()
        component = Component.query.filter_by(name=row["COMPONENT"]).first()
        group = MyGroup.query.filter_by(name=row["GROUP"]).first()

        if not soi:
            error_message = f"SOI '{row['SOI']}' not found in the database."
            break
        if not component:
            error_message = f"Component '{row['COMPONENT']}' not found in the database."
            break
        if not group:
            error_message = f"Group '{row['GROUP']}' not found in the database."
            break

        new_product_group = MyGroupProduct(
            my_group_id=group.id,
            soi_id=soi.id,
            component_id=component.id,
        )
        db.session.add(new_product_group)
        db.session.commit()
    else:
        return "All groups processed successfully."

    return error_message


def create_soi_table(sois):
    soi_groups = [query_group_name("soi", soi.id) for soi in sois]
    soi_table = pd.DataFrame(
        {
            "SOI": [x.name for x in sois],
            "MATERIAL_NUMBER": [x.material_number for x in sois],
            "DESCRIPTION": [x.description for x in sois],
            "STATUS": [x.status for x in sois],
            "DUMMY": [x.dummy for x in sois],
            "CHECK": [x.check for x in sois],
            "GROUP": soi_groups,
            "NOTE": [x.note for x in sois],
            "LAST_COMMENT": [
                x.text if x is not None else ""
                for x in last_comment(table="soi", products=sois)
            ],
        }
    )
    return soi_table


def create_component_table(components):
    component_groups = [query_group_name("component", soi.id) for soi in components]
    component_table = pd.DataFrame(
        {
            "COMPONENT": [x.name for x in components],
            "CODENUMBER": [x.codenumber for x in components],
            "MATERIAL_NUMBER": [x.material_number for x in components],
            "DESCRIPTION": [x.description for x in components],
            "SUPPLIER": [x.supplier for x in components],
            "STATUS": [x.status for x in components],
            "CHECK": [x.check for x in components],
            "GROUP": component_groups,
            "NOTE": [x.note for x in components],
            "LAST_COMMENT": [
                x.text if x is not None else ""
                for x in last_comment(table="component", products=components)
            ],
        }
    )
    return component_table


def create_group_table(groups):
    group_table = pd.DataFrame(
        {
            "GROUP": [x.name for x in groups],
            "STATUS": [x.status for x in groups],
            "CHECK": [x.check for x in groups],
            "NOTE": [x.note for x in groups],
            "LAST_COMMENT": [
                x.text if x is not None else ""
                for x in last_comment(table="my_group", products=groups)
            ],
        }
    )
    return group_table


def create_system_table(systems):
    system_table = pd.DataFrame(
        {
            "SYSTEM": [x.name for x in systems],
            "STATUS": [x.status for x in systems],
            "CHECK": [x.check for x in systems],
            "NOTE": [x.note for x in systems],
            "LAST_COMMENT": [
                x.text if x is not None else ""
                for x in last_comment(table="system", products=systems)
            ],
        }
    )
    return system_table


def create_bom_table(bom_data):
    bom = pd.DataFrame(
        {
            "SOI": [
                SOI.query.filter_by(id=row.soi_joint).first().name for row in bom_data
            ],
            "COMPONENT": [
                Component.query.filter_by(id=row.comp_joint).first().name
                for row in bom_data
            ],
            "USAGE": [row.usage for row in bom_data],
            "MAIN": [row.main for row in bom_data],
        }
    )
    return bom


def create_system_soi_table(system_soi_data):
    system_soi = pd.DataFrame(
        {
            "SYSTEM": [
                System.query.filter_by(id=row.system_joint).first().name
                for row in system_soi_data
            ],
            "SOI": [
                SOI.query.filter_by(id=row.soi_joint).first().name
                for row in system_soi_data
            ],
        }
    )
    return system_soi


def query_group_name(what_type, product_id):
    if what_type == "soi":
        what_group = MyGroupProduct.query.filter_by(soi_id=product_id).first()
    if what_type == "component":
        what_group = MyGroupProduct.query.filter_by(component_id=product_id).first()
    if what_group:
        group = MyGroup.query.filter_by(id=what_group.my_group_id).first().name
    else:
        group = "NA"
    return group


# def last_comment(table, products):
#     table_name = tables_dict.get(table)
#     product_id = [x.id for x in products]
#     all_comments = [
#         db.session.query(table_name).filter_by(id=x).first().comments
#         for x in product_id
#     ]
#     last_comments = [x[-1] if x else None for x in all_comments]
#     return last_comments
