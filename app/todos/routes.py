from app import db

from flask import redirect, request, render_template, flash

from app.todos import todos
from app.models import Todo
from app.forms import AddTodo


@todos.route("/todo/<what_view>", methods=["GET", "POST"])
def todo_view(what_view):
    todos = Todo.query.filter_by(completed=False).all()
    form = AddTodo()

    if what_view.lower() == "completed_false":
        todos = Todo.query.filter_by(completed=False).all()
    if what_view.lower() == "completed_true":
        todos = Todo.query.filter_by(completed=True).all()

    if form.validate_on_submit():
        new_todo = Todo(
            text=form.text.data,
            priority=form.priority.data,
            deadline=form.deadline.data,
        )
        db.session.add(new_todo)
        db.session.commit()
        flash(f"New TODO added")
        return redirect(request.referrer)
    return render_template("todo.html", title="Todo", todos=todos, form=form)


@todos.route("/todo/<id>/change_status", methods=["GET", "POST"])
def change_status_todo(id):
    todo = Todo.query.get(id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(request.referrer)


@todos.route("/todo/<id>/remove", methods=["GET", "POST"])
def remove_todo(id):
    db.session.query(Todo).filter_by(id=id).delete()
    db.session.commit()
    return redirect(request.referrer)
