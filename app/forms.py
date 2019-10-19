'''
class for holding info for the query form on the /index page
'''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class QueryForm(FlaskForm):
    '''
    class for holding info for the query form on the /index page
    '''
    server_ip = StringField('Server ip', validators=[DataRequired()])
    server_port = StringField('Query port', validators=[DataRequired()])
    submit = SubmitField('Enter')