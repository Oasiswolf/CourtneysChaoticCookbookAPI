import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    servings = db.Column(db.Integer)
    image_url = db.Column(db.Text)
    instructions = db.Column(db.Text)

    ingredients = db.relationship("Ingredient", backref="recipe", lazy=True, cascade="all, delete-orphan")
    time = db.relationship("Time", backref="recipe", uselist=False, lazy=True, cascade="all, delete-orphan")


class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.String(200), nullable=False)

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)


class Time(db.Model):
    __tablename__ = "times"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    prep = db.Column(db.Integer)
    cook = db.Column(db.Integer)
    active = db.Column(db.Integer)
    inactive = db.Column(db.Integer)
    ready = db.Column(db.Integer)
    total = db.Column(db.Integer)

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")


one_user_schema = UserSchema()
multi_user_schema = UserSchema(many=True)


class IngredientSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "quantity", "recipe_id")


one_ingredient_schema = IngredientSchema()
multi_ingredient_schema = IngredientSchema(many=True)


class TimeSchema(ma.Schema):
    class Meta:
        fields = ("id", "prep", "cook", "active", "inactive", "ready", "total")


one_time_schema = TimeSchema()
multi_time_schema = TimeSchema(many=True)


class RecipeSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "servings", "image_url", "instructions", "ingredients", "time")

    ingredients = ma.Nested(multi_ingredient_schema)
    time = ma.Nested(one_time_schema)
