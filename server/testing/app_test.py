import json
import pytest
from app import app
from models import db, Plant

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def app_context():
    with app.app_context():
        yield

@pytest.fixture
def plant_obj(app_context):
    plant = Plant(
        name="Douglas Fir",
        image="https://example.com/douglas-fir.jpg",
        price=99.99
    )
    db.session.add(plant)
    db.session.commit()
    yield plant
    db.session.delete(plant)
    db.session.commit()

class TestPlant:
    def test_plants_get_route(self, client):
        '''has a resource available at "/plants".'''
        response = client.get('/plants')
        assert response.status_code == 200

    def test_plants_get_route_returns_list_of_plant_objects(self, client, plant_obj):
        '''returns JSON representing Plant objects at "/plants".'''
        response = client.get('/plants')
        data = json.loads(response.data.decode())
        assert isinstance(data, list)
        for record in data:
            assert isinstance(record, dict)
            assert 'id' in record
            assert 'name' in record

    def test_plants_post_route_creates_plant_record_in_db(self, client, app_context):
        '''allows users to create Plant records through the "/plants" POST route.'''
        payload = {
            "name": "Live Oak",
            "image": "https://example.com/live-oak.jpg",
            "price": 250.00,
        }
        response = client.post('/plants', json=payload)
        assert response.status_code == 201

        # Verify in DB
        lo = db.session.query(Plant).filter_by(name="Live Oak").first()
        assert lo is not None
        assert lo.name == payload["name"]
        assert lo.image == payload["image"]
        assert lo.price == payload["price"]

        # Cleanup
        db.session.delete(lo)
        db.session.commit()

    def test_plant_by_id_get_route(self, client, plant_obj):
        '''has a resource available at "/plants/<int:id>".'''
        response = client.get(f'/plants/{plant_obj.id}')
        assert response.status_code == 200

    def test_plant_by_id_get_route_returns_one_plant(self, client, plant_obj):
        '''returns JSON representing one Plant object at "/plants/<int:id>".'''
        response = client.get(f'/plants/{plant_obj.id}')
        data = json.loads(response.data.decode())
        assert isinstance(data, dict)
        assert data["id"] == plant_obj.id
        assert data["name"] == plant_obj.name

    def test_can_be_created(self, app_context):
        '''can create records that can be committed to the database.'''
        plant = Plant(
            name="Douglas Fir",
            image="https://example.com/douglas-fir.jpg",
            price=99.99
        )
        db.session.add(plant)
        db.session.commit()

        fetched = db.session.get(Plant, plant.id)
        assert fetched is not None
        assert fetched.name == "Douglas Fir"
        assert fetched.image == "https://example.com/douglas-fir.jpg"
        assert fetched.price == 99.99

        db.session.delete(fetched)
        db.session.commit()
