"""
Formulários Flask-WTF
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField


class BaseForm(FlaskForm):
    """Formulário base com CSRF token"""
    csrf_token = HiddenField()
