#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Restaurants(Resource):
    def get(self):
        try:
            data = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in Restaurant.query]
            return data, 200
        
        except Exception as e:
            return str(e), 404

class RestaurantById(Resource):
    def get(self,id):
            try:
                data = Restaurant.query.filter(Restaurant.id == id).first()

                if isinstance(data, Restaurant):
                    return data.to_dict(rules=('restaurant_pizzas',)), 200
                else:
                    return {"error" : "Restaurant not found"}, 404
                
            except Exception as e:
                return str(e), 404
            
    def delete(self,id):
        try:
            data = Restaurant.query.filter(Restaurant.id == id).first()

            if isinstance(data, Restaurant):
                db.session.delete(data)
                db.session.commit()
                return '', 204
            else:
                return {'error': 'restaurant not found'}, 404

        except Exception as e:
            return str(e), 404
            
class Pizzas(Resource):
    def get(self):
        try:
            data = [Pizza.to_dict(rules=('-restaurant_pizzas',)) for Pizza in Pizza.query]
            return data, 200
        
        except Exception as e:
            return str(e), 404

class PizzaById(Resource):
    def get(self,id):
        try:
            data = Pizza.query.filter(Pizza.id == id).first()

            if isinstance(data, Pizza):
                return data.to_dict(only=('id','ingredients','name',)), 200
            else:
                return {"error" : "Pizza not found"}, 404
            
        except Exception as e:
            return str(e), 404

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_rp = RestaurantPizza(**data)
            if isinstance(new_rp, RestaurantPizza):
                db.session.add(new_rp)
                db.session.commit()
                return new_rp.to_dict(only=('id','price','restaurant_id','pizza_id','pizza','restaurant')), 201
            else:
                return {'errors': ['validation errors']}, 400

        except Exception as e:
            return {'errors': ['validation errors']}, 400




api.add_resource(Restaurants, '/restaurants')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(PizzaById, '/pizzas/<int:id>')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
