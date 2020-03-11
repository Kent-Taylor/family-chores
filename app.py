from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku


app = Flask(__name__)
heroku = Heroku(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Todo(db.Model):
    __tablename__ = "todos"
    done = db.Column(db.Boolean)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)

    def __init__(self, title, done, category):
        self.title = title
        self.done = done
        self.category = category

class TodoSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "done", "category")

todos_schema = TodoSchema(many=True)
todo_schema = TodoSchema()

@app.route("/todos", methods=["GET"])
def get_todos():
    all_todos = Todo.query.all()
    result = todos_schema.dump(all_todos)

    return jsonify(result.data)

@app.route("/add-todo", methods=["POST"])
def add_todo():
    title = request.json["title"]
    done = request.json["done"]
    category = request.json["category"]

    record = Todo(title, done, category)
    db.session.add(record)
    db.session.commit()

    todo = Todo.query.get(record.id)
    return todo_schema.jsonify(todo)


@app.route("/todo/<id>", methods=["PUT"])
def update_todo(id):
    todo = Todo.query.get(id)

    title = request.json["title"]
    done = request.json["done"]
    category = request.json["category"]

    todo.title = title
    todo.done = done
    todo.category = category

    db.session.commit()
    return jsonify("UPDATE Successful")

@app.route("/todo/<id>", methods=["DELETE"])
def delete_todo(id):
    record = Todo.query.get(id)
    db.session.delete(record)
    db.session.commit()

    return jsonify("Record DELETED!")



if __name__ == "__main__":
    app.debug = True
    app.run()