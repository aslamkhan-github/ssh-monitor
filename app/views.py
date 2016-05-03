from app import app
from flask import render_template
from task_parser import TaskParser

TASK_DIR = 'task_dir/'


@app.route('/')
@app.route('/index')
def index():
    taskparser = TaskParser(TASK_DIR)
    taskparser.parse()
    return render_template('index.html', task_list=taskparser.task_list)
