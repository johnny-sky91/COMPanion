from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Length

from app.models import (
    SOI,
    SOI_Comment,
    Component,
    Component_Comment,
    System,
    System_Comment,
)


class AddSystem(FlaskForm):
    system_name = TextAreaField(
        "System name", validators=[DataRequired(message="System name can't be empty")]
    )
    submit = SubmitField("Add new System")


class AddSOI(FlaskForm):
    soi_name = TextAreaField(
        "SOI name", validators=[DataRequired(message="SOI name can't be empty")]
    )
    soi_status = TextAreaField(
        "SOI Status", validators=[DataRequired(message="System status can't be empty")]
    )
    submit = SubmitField("Add new SOI")


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
        "Status", validators=[DataRequired(message="Component status can't be empty")]
    )
    submit = SubmitField("Change component status")


class AddComponentComment(FlaskForm):
    component_comment_text = TextAreaField(
        "New comment", validators=[DataRequired(message="Comment text can't be empty")]
    )
    submit = SubmitField("Add new comment")
