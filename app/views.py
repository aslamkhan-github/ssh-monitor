from app import app
from flask import render_template, redirect, url_for

from forms import TaskForm
from filemodel import FileModel


@app.route('/')
def index():
    model = FileModel()
    return render_template('index.html',
                           task_list=model.get_all_task())


@app.route('/task')
def task():
    model = FileModel()
    form = TaskForm()
    return render_template('task.html',
                           scripts=model.get_all_scripts(),
                           form=form)


@app.route('/delete/<id>')
def delete(id):
    model = FileModel()
    model.delete(id)
    return redirect(url_for('index'))
