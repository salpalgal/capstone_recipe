from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    

class SignUpForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()])
    password = PasswordField("password", validators = [Length(min = 6)])
    email = StringField("email", validators = [DataRequired(), Email()])
    image_url = StringField("image_url")


class LoginForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()])
    password = PasswordField("password", validators = [Length(min = 6)])

class RecipeSearchForm(FlaskForm):
    ingredients = TextAreaField("ingredients", validators = [DataRequired()])
    number = IntegerField("number", validators= [DataRequired(), NumberRange(min = 1, max = 5)])