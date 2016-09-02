import datetime
import os.path
from flask import Flask, g, redirect, request, session, url_for, abort, render_template, flash
from functools import wraps
from peewee import *

DATABASE = "homework.db"
DEBUG = True
SECRET_KEY = "sumthineffinrandomshiet"
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


@app.route("/")
def homepage():
    return userstory_list()


def object_list(template_name, qr, var_name="object_list", **kwargs):
    kwargs.update(page=int(request.args.get("page", 1)), pages=(qr.count()-1) // 5 + 1)
    kwargs[var_name] = qr.paginate(kwargs["page"], 5)
    return render_template(template_name, **kwargs)


@app.route("/list/")
def userstory_list():
    return object_list("list.html", UserStory.select(), "story_list")


@app.route("/story/", methods=["GET", "POST"])
def new_userstory():
    if request.method == "POST" and all(request.form.to_dict().values()):
        user_story = UserStory.create(**request.form.to_dict())
        flash("User Story created!")
        return redirect(url_for("homepage"))
    return render_template("form.html", story="", submit="Create")


@app.route("/story/<story_id>", methods=["GET", "POST"])
def update_userstory(story_id):
    if request.method == "POST" and all(request.form.to_dict().values()):
        UserStory.update(**request.form.to_dict()).where(UserStory.id == story_id).execute()
        flash("User Story updated!")
        return redirect(url_for("homepage"))
    return render_template("form.html", story=UserStory.get(UserStory.id == story_id), submit="Update")


@app.route("/delete/<story_id>", methods=["GET"])
def delete_userstory(story_id):
    UserStory.delete().where(UserStory.id == story_id).execute()
    flash("User Story deleted!")
    return redirect(url_for("homepage"))


if __name__ == "__main__":
    if not os.path.isfile("homework.db"):
        create_tables()
    app.run()
