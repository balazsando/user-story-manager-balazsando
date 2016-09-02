import datetime
import os.path
from flask import Flask, g, redirect, request, session, url_for, abort, render_template, flash
from functools import wraps
from peewee import *

DATABASE = 'homework.db'
DEBUG = True
SECRET_KEY = 'sumthineffinrandomshiet'
app = Flask(__name__)
app.config.from_object(__name__)
database = SqliteDatabase(DATABASE)
# database = PostgresqlDatabase("your_db")


class BaseModel(Model):
    class Meta:
        database = database


class UserStory(BaseModel):
    story_title = CharField()
    user_story = TextField()
    acceptance_criteria = TextField()
    business_value = IntegerField()
    estimation = FloatField()
    status = IntegerField()


def create_tables():
    database.connect()
    database.create_tables([UserStory])


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def homepage():
    return userstory_list()


def object_list(template_name, qr, var_name='object_list', **kwargs):
    kwargs.update(page=int(request.args.get('page', 1)), pages=(qr.count()-1) // 5 + 1)
    kwargs[var_name] = qr.paginate(kwargs['page'], 5)
    return render_template(template_name, **kwargs)


@app.route('/list/')
def userstory_list():
    return object_list('list.html', UserStory.select(), 'story_list')


@app.route('/story/', methods=['GET', 'POST'])
def new_userstory():
    fields = ["story_title", "user_story", "acceptance_criteria", "business_value", "estimation", "status"]
    kwargs = {"_data": {"submit": 'Create', "title": "Add new"}}
    if request.method == "POST" and all([request.form[i] for i in fields]):
        data = {i: request.form[i] for i in fields}
        if request.args.get("story_id"):
            UserStory.update(**data).where(UserStory.id == request.args.get("story_id")).execute()
            flash('User Story updated!')
        else:
            user_story = UserStory.create(**data)
            flash('New User Story added!')
        return redirect(url_for('homepage'))
    elif request.args.get('story_id'):
        kwargs.update(UserStory.get(UserStory.id == request.args.get("story_id")).__dict__)
        kwargs['_data']['submit'], kwargs['_data']["title"] = "Update", "Update"
    return render_template('form.html', **kwargs['_data'])


@app.route('/delete/', methods=['GET'])
def delete_userstory():
    UserStory.delete().where(UserStory.id == request.args.get("story_id")).execute()
    flash('User Story deleted!')
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    if not os.path.isfile("homework.db"):
        create_tables()
    app.run()
