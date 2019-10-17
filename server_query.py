import os
from flask import render_template
from flask import Flask
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class QueryForm(FlaskForm):
    query = StringField('Server query', validators=[DataRequired()])
    submit = SubmitField('Enter Ip')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('CSRF_KEY')

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Test'}
    return render_template('index.html', title='Home', user=user)

@app.route('/query')
def query():
    form = QueryForm()
    return render_template('query.html', title='Query', form=form)

@app.route('/query=<server_ip>')
def displayServer(server_ip):
    