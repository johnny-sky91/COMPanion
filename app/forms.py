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
    system_name = TextAreaField(
        "System name", validators=[DataRequired(message="System name can't be empty")]
    )
    submit = SubmitField("Add new System")


class AddSOI(FlaskForm):
    soi_name = TextAreaField(
        "Name", validators=[DataRequired(message="SOI name can't be empty")]
    )
    soi_description = TextAreaField(
        "Description",
        validators=[DataRequired(message="SOI Description can't be empty")],
    )
    soi_status = SelectField(
        "Status", validators=[DataRequired(message="SOI status can't be empty")]
    )
    submit = SubmitField("Add new SOI")


class ChangeSoiStatus(FlaskForm):
    soi_status = SelectField(
        "New status",
        validators=[DataRequired(message="SOI status can't be empty")],
    )
    submit = SubmitField("Change SOI status")


class AddComponent(FlaskForm):
    component_name = TextAreaField(
        "Name", validators=[DataRequired(message="Component name can't be empty")]
    )
    component_description = TextAreaField(
        "Description",
        validators=[DataRequired(message="Component Description can't be empty")],
    )
    component_status = SelectField(
        "Status", validators=[DataRequired(message="Component status can't be empty")]
    )
    submit = SubmitField("Add new component")


class ChangeComponentStatus(FlaskForm):
    component_status = SelectField(
        "New status",
        validators=[DataRequired(message="Component status can't be empty")],
    )
    submit = SubmitField("Change component status")


class AddComponentComment(FlaskForm):
    component_comment_text = TextAreaField(
        "New comment", validators=[DataRequired(message="Comment text can't be empty")]
    )
    submit = SubmitField("Add new comment")
