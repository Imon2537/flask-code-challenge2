#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

# Base directory setup and database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migration
migrate = Migrate(app, db)
db.init_app(app)

# API instance setup
api = Api(app)


# Route for the index page
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


# Route to GET all restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])


# Route to GET a specific restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict())
    else:
        return jsonify({"error": "Restaurant not found"}), 404


# Route to DELETE a restaurant by ID (and cascade delete RestaurantPizzas)
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)  # No content response
    else:
        return jsonify({"error": "Restaurant not found"}), 404


# Route to GET all pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])


# Route to POST a new RestaurantPizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    # Validate price
    if 'price' not in data or not (1 <= data['price'] <= 30):
        return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

    # Ensure that the provided restaurant and pizza exist
    restaurant = Restaurant.query.get(data.get('restaurant_id'))
    pizza = Pizza.query.get(data.get('pizza_id'))
    
    if not restaurant or not pizza:
        return jsonify({"errors": ["Restaurant or Pizza not found"]}), 404
    
    try:
        # Create new RestaurantPizza
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            restaurant_id=data['restaurant_id'],
            pizza_id=data['pizza_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        
        return jsonify(new_restaurant_pizza.to_dict()), 201  # Created response
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
