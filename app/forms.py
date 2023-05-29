from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    TextAreaField,
    BooleanField,
    IntegerField,
)
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError
from app.models import Component, SOI, System


class AddComponent(FlaskForm):
    name = TextAreaField(
        "Name", validators=[DataRequired(message="Component name can't be empty")]
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(message="Component Description can't be empty")],
    )
    supplier = TextAreaField(
        "Supplier",
        validators=[DataRequired(message="Component Supplier can't be empty")],
    )
    status = SelectField(
        "Status", validators=[DataRequired(message="Component status can't be empty")]
    )
    submit = SubmitField("Add new component")

    def validate_name(self, field):
        name = field.data
        component = Component.query.filter_by(name=name).first()
        if component:
            raise ValidationError("Component is already registered")


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

    def validate_name(self, field):
        name = field.data
        soi = SOI.query.filter_by(name=name).first()
        if soi:
            raise ValidationError("SOI is already registered")


class AddSystem(FlaskForm):
    name = TextAreaField(
        "System name",
        validators=[DataRequired(message="System name can't be empty")],
    )
    status = SelectField(
        "Status", validators=[DataRequired(message="System status can't be empty")]
    )
    submit = SubmitField("Add new System")

    # TODO fix validator
    def validate_name(self, field):
        name = field.data
        system = System.query.filter_by(name=name).first()
        if system:
            raise ValidationError("System is already registered")


class ChangeStatus(FlaskForm):
    status = SelectField(
        "New status",
        validators=[DataRequired(message="Status can't be empty")],
    )
    submit = SubmitField("Change status")


class AddProductComment(FlaskForm):
    text = TextAreaField(
        "New comment",
        validators=[DataRequired(message="Comment text can't be empty")],
    )
    submit = SubmitField("Add new comment")


class AddCompSoi(FlaskForm):
    component = TextAreaField(
        "Component",
        validators=[DataRequired(message="Choose component")],
    )
    usage = IntegerField(
        "Usage",
        validators=[InputRequired(message="Choose usage"), NumberRange(min=1, max=12)],
    )
    main = BooleanField(
        "Main?",
        validators=[],
    )
    submit = SubmitField("Add component to SOI")


class AddSystemSOI(FlaskForm):
    system = SelectField(
        "What system",
        validators=[DataRequired(message="Choose system")],
    )
    submit = SubmitField("Add system to SOI")


class SearchProduct(FlaskForm):
    product = StringField("Search product", validators=[DataRequired()])
    submit = SubmitField("Search")
