from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class QueryForm(FlaskForm):
    server_ip = StringField('Server ip', validators=[DataRequired()])
    server_port = StringField('Query port', validators=[DataRequired()])
    submit = SubmitField('Enter')