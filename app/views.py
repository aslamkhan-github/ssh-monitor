from app import app
from flask import render_template, redirect, url_for
from task_parser import TaskParser
import os

TASK_DIR = 'task_dir/'


@app.route('/')
def index():
    taskparser = TaskParser(TASK_DIR)
    taskparser.parse()
    return render_template('index.html',
                           task_list=taskparser.task_list)


@app.route('/task')
def task():
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete(id):
    path = os.path.join(TASK_DIR, id + '.yml')
    print 'deleting ' + path
    os.remove(path)
    return redirect(url_for('index'))
