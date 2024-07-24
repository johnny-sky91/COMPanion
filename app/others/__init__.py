from flask import Blueprint

others = Blueprint("others", __name__, template_folder="templates")

from app.others import routes
