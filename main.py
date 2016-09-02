import os.path
from flask import Flask, g, redirect, request, url_for, render_template, flash
from peewee import *

DATABASE = "user_story_manager.db"
DEBUG = True
SECRET_KEY = "sumthineffinrandomshiet"
app = Flask(__name__)
app.config.from_object(__name__)
database = SqliteDatabase(DATABASE)
# database = PostgresqlDatabase("your_db")


class UserStory(Model):
    story_title = CharField()
    user_story = TextField()
    acceptance_criteria = TextField()
    business_value = IntegerField()
    estimation = FloatField()
    status = IntegerField()

    class Meta:
        database = database
        order_by = ["status", "-business_value"]


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
    return list_userstory()


@app.route("/list/")
@app.route("/list/<int:page>")
def list_userstory(page=1):
    kwargs = {"page": page,
              "pages": UserStory.select().count() / 10,
              "story_list": UserStory.select().paginate(page, 10)}
    return render_template("list.html", **kwargs)


@app.route("/story/", methods=["GET", "POST"])
def create_userstory():
    if request.method == "POST" and all(request.form.to_dict().values()):
        UserStory.create(**request.form.to_dict())
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
    if not os.path.isfile(DATABASE):
        create_tables()
    app.run()
