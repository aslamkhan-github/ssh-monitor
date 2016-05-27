from flask_wtf import Form
from wtforms import StringField, DecimalField
from wtforms.validators import DataRequired


class TaskForm(Form):
    id = StringField('ID', validators=[DataRequired()])
    host = StringField('Host', validators=[DataRequired()])
    user = StringField('User', validators=[DataRequired()])
    passwd = StringField('Pass', validators=[DataRequired()])
    task = StringField('Task', validators=[DataRequired()])
    interval = DecimalField('Interval', validators=[DataRequired()])
    disks = StringField('Disks')
    db_host = StringField('Graphite Host', validators=[DataRequired()])
    db_port = StringField('Graphite Port', validators=[DataRequired()])
    path = StringField('Graphite Path', validators=[DataRequired()])
