from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Length

from app.models import (
    SOI,
    SoiComment,
    Component,
    ComponentComment,
    System,
    SystemComment,
)


class AddSystem(FlaskForm):
    name = TextAreaField(
        "System name", validators=[DataRequired(message="System name can't be empty")]
    )
    status = SelectField(
        "Status", validators=[DataRequired(message="System status can't be empty")]
    )
    submit = SubmitField("Add new System")


class ChangeSystemStatus(FlaskForm):
    status = SelectField(
        "New status",
        validators=[DataRequired(message="System status can't be empty")],
    )
    submit = SubmitField("Change system status")


class AddSystemComment(FlaskForm):
    text = TextAreaField(
        "New comment", validators=[DataRequired(message="Comment text can't be empty")]
    )
    submit = SubmitField("Add new comment")


class AddSOI(FlaskForm):
    name = TextAreaField(
        "Name", validators=[DataRequired(message="SOI name can't be empty")]
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(message="SOI Description can't be empty")],
    )
    status = SelectField(
        "Status", validators=[DataRequired(message="SOI status can't be empty")]
    )
    submit = SubmitField("Add new SOI")


class ChangeSoiStatus(FlaskForm):
    status = SelectField(
        "New status",
        validators=[DataRequired(message="SOI status can't be empty")],
    )
    submit = SubmitField("Change SOI status")


class AddSoiComment(FlaskForm):
    text = TextAreaField(
        "New comment", validators=[DataRequired(message="Comment text can't be empty")]
    )
    submit = SubmitField("Add new comment")


class AddComponent(FlaskForm):
    name = TextAreaField(
        "Name", validators=[DataRequired(message="Component name can't be empty")]
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(message="Component Description can't be empty")],
    )
    status = SelectField(
        "Status", validators=[DataRequired(message="Component status can't be empty")]
    )
    submit = SubmitField("Add new component")


class ChangeComponentStatus(FlaskForm):
    status = SelectField(
        "New status",
        validators=[DataRequired(message="Component status can't be empty")],
    )
    submit = SubmitField("Change component status")


class AddComponentComment(FlaskForm):
    text = TextAreaField(
        "New comment", validators=[DataRequired(message="Comment text can't be empty")]
    )
    submit = SubmitField("Add new comment")


class AddCompSoi(FlaskForm):
    component = SelectField(
        "What component",
        validators=[DataRequired(message="Choose component")],
    )
    submit = SubmitField("Add component to SOI")
