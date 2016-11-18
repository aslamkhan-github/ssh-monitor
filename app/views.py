from app import app
from flask import request
from flask import render_template, redirect, url_for

from filemodel import FileModel


@app.route('/')
def index():
    model = FileModel()
    task_list = model.get_all_task()
    task_list.sort(key=lambda x: x.host)
    inactives = model.get_all_inactives()
    inactives.sort()
    return render_template('index.html',
                           task_list=task_list,
                           inactives=inactives)


@app.route('/log')
def log():
    with open('/mnt/data/supervisor/ssh-monitor.log', 'r') as f:
        log = f.read()

    return render_template('log.html', log=log)


@app.route('/task')
def new_task():
    model = FileModel()
    task = model.get_template()
    return render_template('new_task.html', task=task)


@app.route('/task', methods=['POST'])
def add_task():
    text = request.form['text']
    id = request.form['id']
    model = FileModel()
    model.update(id, text)
    return redirect(url_for('index'))


@app.route('/task/<id>')
def task(id):
    model = FileModel()
    task = model.get_task(id)
    return render_template('edit_task.html', task=task, id=id)


@app.route('/inactive/<id>')
def inactive(id):
    model = FileModel()
    task = model.get_inactive(id)
    return render_template('inactive.html', task=task, id=id)


@app.route('/inactive/<id>', methods=['POST'])
def activate(id):
    model = FileModel()
    model.activate(id)
    return redirect(url_for('index'))


@app.route('/task/<id>', methods=['POST'])
def update(id):
    text = request.form['text']
    model = FileModel()
    model.update(id, text)
    task = model.get_task(id)
    return render_template('edit_task.html', task=task, id=id)


@app.route('/disable/<id>')
def disable(id):
    model = FileModel()
    model.disable(id)
    return redirect(url_for('index'))


@app.route('/delete/<id>')
def delete(id):
    model = FileModel()
    model.delete(id)
    return redirect(url_for('index'))
