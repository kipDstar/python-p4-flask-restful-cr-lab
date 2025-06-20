#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        # Return as a list with status code
        return [plant.to_dict() for plant in plants], 200

    def post(self):
        try:
            data = request.get_json()

            # Ensure data contains required fields
            if not data or not all(k in data for k in ('name', 'image', 'price')):
                return {"error": "Missing data"}, 400

            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=data['price']
            )

            db.session.add(new_plant)
            db.session.commit()

            return new_plant.to_dict(), 201

        except (TypeError, KeyError):
            return {"error": "Invalid data format"}, 400

api.add_resource(Plants, '/plants')


class PlantByID(Resource):
    def get(self, id):
        plant = db.session.get(Plant, id)
        if not plant:
            return {"error": "Plant not found"}, 404
        return plant.to_dict(), 200

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
