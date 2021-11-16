from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    IntegerField,
    SelectField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User, Classes


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    user_type = SelectField(u'Register as', choices=[('teacher', 'Teacher'), ('student', 'Student') ])


    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    
class PostForm(FlaskForm):
    class_name = StringField("Course Name", validators=[DataRequired()])
    time = SelectField(u'Time', choices=[('8:00-9:00 am', '8:00-9:00 am'),('9:00-10:00 am', '9:00-10:00 am'),('10:00-11:00 am', '10:00-11:00 am'),('11:00-12:00 pm', '11:00-12:00 pm'),('12:00-13:00 pm', '12:00-13:00 pm'),('13:00-14:00 pm', '13:00-14:00 pm'),('14:00-15:00 pm', '14:00-15:00 pm'),('15:00-16:00 pm', '15:00-16:00 pm'),('16:00-17:00 pm', '16:00-17:00 pm'), ])
    limit = IntegerField('Enrollment Limit',validators=[DataRequired()])


    submit = SubmitField("Submit")
    
    def validate_class_name(self, class_name):
            class_name = Classes.query.filter_by(class_name=class_name.data).first()
            if class_name:
                raise ValidationError(
                    "This Class Name is taken. Please choose a different one."
                )
