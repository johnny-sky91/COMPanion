from flask import Blueprint

todos = Blueprint("todo", __name__, template_folder="templates")

from app.todos import routes
