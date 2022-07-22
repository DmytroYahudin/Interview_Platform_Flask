from flask_wtf import FlaskForm
from wtforms import (
    DecimalField,
    FieldList,
    Form,
    FormField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    Regexp,
)
from wtforms.widgets import CheckboxInput, ListWidget, TableWidget
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from ..models import Candidate, Question, Role, User


class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class InterviewerRegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or " "underscores",
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class CandidateForm(FlaskForm):
    first_name = StringField("Enter candidate name", validators=[DataRequired()])
    last_name = StringField("Enter candidate lastname", validators=[DataRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(1, 64), Email()])
    skills = StringField("Skills", validators=[InputRequired(), Length(1, 128)])
    about = StringField("About", validators=[Length(1, 256)])
    submit = SubmitField("Submit")


class QuestionForm(FlaskForm):
    question_text = StringField(
        "Enter question text", validators=[DataRequired(), Length(1, 256)]
    )
    weight = DecimalField("Enter question weight in range 0..1", default=1, places=2)
    submit = SubmitField("Submit")


def candidate_choice():
    return Candidate.query


def interviewer_choice():
    role = Role.query.filter_by(role_name="interviewer").first()
    return User.query.filter_by(role_id=role.id)


def question_choice():
    return Question.query


class InterviewForm(FlaskForm):
    candidate_id = QuerySelectField(
        "Candidate", get_label="first_name", allow_blank=False
    )
    interviewer = QuerySelectMultipleField(
        "Interviewer", get_label="username", allow_blank=False
    )
    question = QuerySelectMultipleField(
        "Question",
        get_label="question_text",
        allow_blank=False,
    )
    # summary = StringField('Summary', validators=[Length(1, 512)])
    submit = SubmitField("Submit")


class Ans(Form):
    mark = IntegerField("mark", validators=[InputRequired()])


class AnswerForm(FlaskForm):
    mark_set = FieldList(FormField(Ans), min_entries=1)
    submit = SubmitField("End Interview")
