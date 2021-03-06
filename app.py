from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
# The Live Web Address for this api
# https://courtneys-chaotic-cookbook-api.herokuapp.com 
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://dimtatlrpvoeti:7c2a0a66d9ee19400602937170f178831d931505d333c998689edd59db98cfc9@ec2-23-23-133-10.compute-1.amazonaws.com:5432/dvebbntrfft51"

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
    text = db.Column(db.Text, nullable=False)

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
        fields = ("id", "username")


one_user_schema = UserSchema()
multi_user_schema = UserSchema(many=True)


class IngredientSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "recipe_id")


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


one_recipe_schema = RecipeSchema()
multi_recipe_schema = RecipeSchema(many=True)

# endpoints

# GET endpoints


@app.route("/recipe/get-all", methods=["GET"])
def get_all_recipes():
    all_recipes = db.session.query(Recipe).all()
    return jsonify(multi_recipe_schema.dump(all_recipes))


@app.route("/recipe/get/<id>", methods=["GET"])
def get_recipe_by_id(id):
    recipe = db.session.query(Recipe).filter(Recipe.id == id).first()
    return jsonify(one_recipe_schema.dump(recipe))


@app.route("/ingredient/get-all", methods=["GET"])
def get_all_ingredients():
    all_ingredients = db.session.query(Ingredient).all()
    return jsonify(multi_ingredient_schema.dump(all_ingredients))


@app.route("/ingredient/get/<id>", methods=["GET"])
def get_ingredient_by_id(id):
    ingredient = db.session.query(Ingredient).filter(Ingredient.id == id).first()
    return jsonify(one_ingredient_schema.dump(ingredient))


@app.route("/user/get", methods=["GET"])
def get_all_users():
    users = db.session.query(User).all()
    return jsonify(multi_user_schema.dump(users))


@app.route("/user/get/<id>", methods=["GET"])
def get_user_by_id(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(one_user_schema.dump(user))


@app.route("/user/get_name/<name>", methods=["GET"])
def get_user_by_name(name):
    user = User.query.filter_by(username=name).first()
    if user == None:
        return jsonify("Error: User not found")
    return jsonify(one_user_schema.dump(user))


@app.route("/time/get/<id>", methods=["GET"])
def get_time_by_id(id):
    times = db.session.query(Time).filter(Time.id == id).first()
    return jsonify(one_time_schema.dump(times))


@app.route("/recipe/random", methods=["GET"])
def get_one_random_recipe():
    recipes = Recipe.query.all()
    return jsonify(one_recipe_schema.dump(random.choice(recipes)))


# POST endpoints


@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json()
    username = data.get("username")
    if User.query.filter_by(username=username).first() != None:
        return jsonify("User already exists")
    password = data.get("password")

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=pw_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(one_user_schema.dump(new_user))


@app.route("/user/verification", methods=["POST"])
def verification():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify("Username not verified")

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify("Username not verified")

    return jsonify("User verified")


@app.route("/recipe/add", methods=["POST"])
def add_recipe():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json().get("values")
    name = data.get("name")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")
    servings = data.get("servings")
    image_url = data.get("image")
    time = data.get("time")

    if name == "":
        return jsonify("Error: Must include a name")

    if servings == "":
        servings = None

    if len(instructions) > 0:
        instructions = "/n".join(instructions)

    new_recipe = Recipe(name=name, servings=servings, image_url=image_url, instructions=instructions)
    db.session.add(new_recipe)
    db.session.commit()

    for ingredient in ingredients:
        print(ingredient)
        new_ingredient = Ingredient(text=ingredient, recipe_id=new_recipe.id)
        db.session.add(new_ingredient)
        db.session.commit()

    new_time = Time(
        prep=time["prep"] if time["prep"] != "" else None,
        cook=time["cook"] if time["cook"] != "" else None,
        active=time["active"] if time["active"] != "" else None,
        inactive=time["inactive"] if time["inactive"] != "" else None,
        ready=time["ready"] if time["ready"] != "" else None,
        total=time["total"] if time["total"] != "" else None,
        recipe_id=new_recipe.id,
    )
    db.session.add(new_time)
    db.session.commit()

    return jsonify(one_recipe_schema.dump(new_recipe))


# PUT endpoints


@app.route("/user/update", methods=["PUT"])
def update_user():
    data = request.get_json()
    id = data.get("id")
    user = User.query.get(id)
    if user == None:
        return jsonify("Error: Invalid user")

    username = data.get("username")
    password = data.get("password")

    if username != None and username != "":
        user.username = username
    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
    db.session.commit()


# DELETE endpoints


@app.route("/recipe/delete/<id>", methods=["DELETE"])
def delete_recipe_by_id(id):
    recipe = Recipe.query.get(id)
    if recipe == None:
        return jsonify("Error: Invalid recipe")
    db.session.delete(recipe)
    db.session.commit()
    return jsonify("Recipe deleted successfully")


@app.route("/user/delete/<id>", methods=["DELETE"])
def delete_user_by_id(id):
    user = User.query.get(id)
    if user == None:
        return jsonify("Error: Invalid user")
    db.session.delete(user)
    db.session.commit()
    return jsonify("User deleted successfully")


if __name__ == "__main__":
    app.run(debug=True)
