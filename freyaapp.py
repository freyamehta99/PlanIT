import datetime
from flask import Flask, flash, redirect, request, render_template, url_for
import peewee as pw
import wtforms as wt
from flask_peewee.auth import Auth
from flask_peewee.db import Database
from utils import slugify

DATABASE = {
    'name': 'test.db',
    'engine': 'peewee.SqliteDatabase',
}

DEBUG = True
SECRET_KEY = 'ssshhhh'

app = Flask(__name__)
app.config.from_object(__name__)
db = Database(app)
auth = Auth(app, db)

# Models
User = auth.get_user_model()


class Task(db.Model):
    task = pw.TextField()
    user = pw.ForeignKeyField(User)
    created = pw.DateTimeField(default=datetime.datetime.now)
    due = pw.DateField()
    #completed = pw.BooleanField(default=False)

    @property
    def tags(self):
        return Tag.select().join(TaskTag).join(Task).where(Task.id == self.id)

    @property
    def statusp(self):
        return Status.select().join(TaskStatus).join(Task).where(Task.id == self.id)


class Tag(db.Model):
    tag = pw.TextField(unique=True)
    

class Status(db.Model):
    status = pw.TextField(unique=True)
    

class TaskTag(db.Model):
    task = pw.ForeignKeyField(Task)
    tag = pw.ForeignKeyField(Tag)


class TaskStatus(db.Model):
    task = pw.ForeignKeyField(Task)
    status = pw.ForeignKeyField(Status)


# Forms
class TaskForm(wt.Form):
    task = wt.TextField([wt.validators.Required()])
    statusp = wt.TextField()
    tags = wt.TextField()
    due = wt.DateField()


# Queries
def user_tasks():
    return Task.select().join(User).where(User.id == auth.get_logged_in_user())


def user_tagged_tasks(tag):
    tagged_tasks = TaskTag.select().join(Tag).where(Tag.tag == tag)
    tasks = Task.select().join(User).where(
        (User.id == auth.get_logged_in_user()) &
        (Task.id << [t.task for t in tagged_tasks]))
    return tasks



def user_statused_tasks(status):
    statused_tasks = TaskStatus.select().join(Status).where(Status.status == status)
    tasks = Task.select().join(User).where(
        (User.id == auth.get_logged_in_user()) &
        (Task.id << [t.task for t in statused_tasks]))
    return tasks

# Views
@app.route("/", methods=['GET'])
@auth.login_required
def home():
    sortby = request.args.get('sortby', 'due')
    if sortby == 'title':
        todos = user_tasks().order_by(Task.task)
    else:
        todos = user_tasks().order_by(Task.due)
    #todos = todos.query.filter_by(complete=False).all()
    #complete = todos.query.filter_by(complete=True).all()
    return render_template('todo.html', todos=todos)
    #return render_template('todo.html', todos=todos,complete=complete)


@app.route('/add', methods=['POST'])
@auth.login_required
def add_task():
    form = TaskForm(request.form)
    if form.validate():
        tags = [slugify(t) for t in form.tags.data.split(' ')]
        statusp = [slugify(t) for t in form.statusp.data.split(' ')]
        new_task = Task(task=form.task.data,
                        user=auth.get_logged_in_user(),
                        due=form.due.data
                        )
        new_task.save()
        for t in tags:
            try:
                new_tag = Tag.get(tag=t)
            except:
                new_tag = Tag(tag=t)
                new_tag.save()
            tasktag = TaskTag(task=new_task.id, tag=new_tag.id)
            tasktag.save()

        for t in statusp:
            try:
                new_status = Status.get(status=t)
            except:
                new_status = Status(status=t)
                new_status.save()
            statustag = TaskStatus(task=new_task.id, status=new_status.id)
            statustag.save()

        flash("New Task: %s" % (new_task.task))
    return redirect(url_for('home'))


@app.route('/del', methods=['POST'])
@auth.login_required
def delete_task():
    tskid = request.form['task']  
    tskobj = Task.get(Task.id == tskid)
    tskobj.delete_instance()
    query = TaskTag.delete().where(TaskTag.task == tskid)
    query2 = TaskStatus.delete().where(TaskStatus.task == tskid)
    query.execute()
    query2.execute()
    flash("Task Completed")
    return redirect(url_for('home'))


@app.route("/status/<status>", methods=['GET'])
def status(status):
    todos = user_statused_tasks(status)
    flash("Tasks labeled %s" % (status, ))
    return render_template('todo.html', todos=todos)



@app.route("/tag/<tag>", methods=['GET'])
def tag(tag):
    todos = user_tagged_tasks(tag)
    flash("Tasks labeled %s" % (tag, ))
    return render_template('todo.html', todos=todos)
#-------------------------------------------------------------------------------------------
#adding a profile here
@app.route('/<username>', methods=['GET'])
@auth.login_required
def user(username):
    #user = User.query.filter_by(username=username).first_or_404()
    #posts = [
     #   {'author': User, 'body': 'Test post #1'},
      #  {'author': User, 'body': 'Test post #2'}
   # ]
    return render_template('profile.html', username=username)
#-----------------------------------------------------------------------------------------------
def drop_all():
    '''create all the tables'''
    auth.User.drop_table(fail_silently=True)
    Task.drop_table(fail_silently=True)
    Tag.drop_table(fail_silently=True)
    TaskTag.drop_table(fail_silently=True)


def create_all():
    '''create all the tables'''
    auth.User.create_table(fail_silently=True)
    Task.create_table(fail_silently=True)
    Tag.create_table(fail_silently=True)
    Status.create_table(fail_silently=True)
    TaskStatus.create_table(fail_silently=True)
    TaskTag.create_table(fail_silently=True)


if __name__ == '__main__':
    # drop_all()
    create_all()
    app.run(port=5005)
