import pytest
from app import app, db, Vehicle

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()

def test_index_page(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Carfax Panam\xc3\xa1" in response.data

def test_report_page_found(client):
    """Test that the report page returns a vehicle that exists."""
    with app.app_context():
        vehicles = [
            Vehicle(plate='AB1234', make='Toyota', model='Corolla', year=2020, accidents=0, owners=1),
            Vehicle(plate='CD5678', make='Honda', model='Civic', year=2019, accidents=1, owners=2)
        ]
        db.session.bulk_save_objects(vehicles)
        db.session.commit()
    response = client.post('/report', data={'plate': 'AB1234'})
    assert response.status_code == 200
    assert b"Reporte del Veh\xc3\xadculo" in response.data
    assert b"AB1234" in response.data
    assert b"Toyota" in response.data

def test_report_page_not_found(client):
    """Test that the report page handles a vehicle that does not exist."""
    response = client.post('/report', data={'plate': 'ZZ9999'})
    assert response.status_code == 200
    assert b"Reporte del Veh\xc3\xadculo" in response.data
    assert b"No se encontr\xc3\xb3 informaci\xc3\xb3n para esta placa." not in response.data # This needs to be implemented
