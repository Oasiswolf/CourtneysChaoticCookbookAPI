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
    recipe = db.session.query(Recipe).filter(Month.id == id).first()
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


@app.route("/time/get/<id>", methods = ["GET"])
def get_all_times(id):
    times = db.session.query(Time).filter(Time.id == id).first()
    return jsonify(one_time_schema.dump(times))


# POST endpoints


@app.route("/recipe/add", methods=["POST"])
def add_recipe():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json()
    name = data.get("name")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")
    servings = data.get("servings")
    image_url = data.get("image")
    time = data.get("time")

    if name == "":
        return jsonify("Error: Must include a name")

    if len(ingredients) == 0:
        return jsonify("Error: Must include ingredients")

    if servings == "":
        servings = None

    if len(instructions) > 0:
        instructions = "/n".join(instructions)

    new_recipe = Recipe(name=name, servings=servings, image_url=image_url, instructions=instructions)
    db.session.add(new_recipe)
    db.session.commit()

    for ingredient in ingredients:
        # parse ingredients in some way
        pass

    new_time = Time(
        prep=time["prep"],
        cook=time["cook"],
        active=time["active"],
        inactive=time["inactive"],
        ready=time["ready"],
        total=time["total"],
        recipe_id=new_recipe.id,
    )
    db.session.add(new_time)
    db.session.commit()

    return jsonify(one_recipe_schema.dump(new_recipe))


# PUT endpoints

# DELETE endpoints



if __name__ == "__main__":
    app.run(debug=True)
