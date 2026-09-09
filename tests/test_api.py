"""Exercise real HTTP routes against a disposable SQLite database."""
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Backend import models
from Backend.auth import COOKIE, token_hash, verify_password
from Backend.database import get_db
from Backend.main import app


@pytest.fixture
def database(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    models.Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def override_db():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    yield factory
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def client(database):
    # Avoid production lifespan: the fixture already created isolated test tables.
    client = TestClient(app)
    yield client
    client.close()


def register(client, suffix="one"):
    return client.post('/api/register', json={
        'email': f'{suffix}@example.com', 'username': suffix, 'password': 'learning-fitlog-123',
    })


def test_account_lifecycle(client, database):
    assert client.get('/api/me').status_code == 401
    response = register(client)
    assert response.status_code == 201
    assert set(response.json()) == {'id', 'email', 'username'}
    assert 'HttpOnly' in response.headers['set-cookie']
    assert 'SameSite=strict' in response.headers['set-cookie']
    with database() as db:
        user = db.query(models.User).one()
        assert user.hashed_password != 'learning-fitlog-123'
        assert verify_password('learning-fitlog-123', user.hashed_password)
    assert client.get('/api/me').json()['username'] == 'one'
    stolen_cookie = client.cookies.get(COOKIE)
    assert client.post('/api/logout', json={}).status_code == 204
    client.cookies.set(COOKIE, stolen_cookie)
    assert client.get('/api/me').status_code == 401
    client.cookies.clear()
    assert client.post('/api/login', json={'email': 'ONE@example.com', 'password': 'incorrect-password'}).status_code == 401
    assert client.post('/api/login', json={'email': 'ONE@example.com', 'password': 'learning-fitlog-123'}).status_code == 200
    assert register(client).status_code == 409


def test_logging_totals_history_and_delete(client):
    register(client)
    food = {'date': '2026-09-09', 'name': 'Lunch', 'calories': 520, 'protein': 40, 'carbs': 60, 'fat': 15}
    response = client.post('/api/foods', json=food)
    assert response.status_code == 201
    food_id = response.json()['id']
    assert client.post('/api/foods', json={**food, 'calories': 100}).status_code == 201
    workout = {'date': food['date'], 'exercise': 'Squat', 'sets': 3, 'reps': 8, 'weight': 135}
    response = client.post('/api/workouts', json=workout)
    assert response.status_code == 201
    workout_id = response.json()['id']
    day = client.get('/api/day?date=2026-09-09').json()
    assert day['totals'] == {'calories': 620, 'protein': 80, 'carbs': 120, 'fat': 30}
    assert day['workouts'][0]['sets'] == 3
    assert client.get('/api/day?date=2026-09-08').json()['foods'] == []
    goals = {'calories': 2300, 'protein': 160, 'carbs': 240, 'fat': 70}
    assert client.put('/api/goals', json=goals).json() == goals
    assert client.get('/api/day?date=2026-09-09').json()['goals'] == goals
    assert client.request('DELETE', f'/api/foods/{food_id}', json={}).status_code == 204
    assert client.request('DELETE', f'/api/workouts/{workout_id}', json={}).status_code == 204
    assert client.get('/api/day?date=2026-09-09').json()['totals']['calories'] == 100
    # A fresh browser can sign in and still see the committed database records.
    client.cookies.clear()
    client.post('/api/login', json={'email': 'one@example.com', 'password': 'learning-fitlog-123'})
    assert len(client.get('/api/day?date=2026-09-09').json()['foods']) == 1


def test_users_cannot_read_or_delete_each_others_entries(client):
    register(client)
    food = client.post('/api/foods', json={'date': '2026-09-09', 'name': 'Private lunch', 'calories': 500}).json()
    workout = client.post('/api/workouts', json={'date': '2026-09-09', 'exercise': 'Private squat', 'sets': 3, 'reps': 8}).json()
    client.post('/api/logout', json={})
    register(client, 'two')
    day = client.get('/api/day?date=2026-09-09').json()
    assert day['foods'] == day['workouts'] == []
    for kind, entry in [('foods', food), ('workouts', workout)]:
        assert client.request('DELETE', f'/api/{kind}/{entry["id"]}', json={}).status_code == 404
    client.put('/api/goals', json={'calories': 3000, 'protein': 100, 'carbs': 100, 'fat': 100})
    client.post('/api/logout', json={})
    client.post('/api/login', json={'email': 'one@example.com', 'password': 'learning-fitlog-123'})
    assert client.get('/api/day?date=2026-09-09').json()['goals']['calories'] == 2000


@pytest.mark.parametrize('path,payload', [
    ('/foods', {'date': 'bad', 'name': 'Lunch', 'calories': 100}),
    ('/foods', {'date': '2026-09-09', 'name': '   ', 'calories': 100}),
    ('/foods', {'date': '2026-09-09', 'name': 'Lunch', 'calories': -1}),
    ('/foods', {'date': '2026-09-09', 'name': 'Lunch', 'calories': 100, 'user_id': 2}),
    ('/workouts', {'date': '2026-09-09', 'exercise': 'Squat', 'sets': 0, 'reps': 10}),
    ('/workouts', {'date': '2026-09-09', 'exercise': 'Squat', 'sets': 2.5, 'reps': 10}),
])
def test_invalid_entries(client, path, payload):
    register(client)
    assert client.post(f'/api{path}', json=payload).status_code == 422


def test_session_expiry(client, database):
    register(client)
    with database() as db:
        session = db.get(models.LoginSession, token_hash(client.cookies.get(COOKIE)))
        session.expires_at = time.time() - 1
        db.commit()
    assert client.get('/api/day?date=2026-09-09').status_code == 401


def test_security_and_static_files(client):
    assert client.get('/').status_code == 200
    assert 'FitLog' in client.get('/').text
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/static/style.css').status_code == 200
    assert client.post('/api/login', data={'email': 'one@example.com'}).status_code == 415
    assert client.post('/api/login', json={}, headers={'Sec-Fetch-Site': 'cross-site'}).status_code == 403
    assert client.post('/api/foods', json={'date': '2026-09-09', 'name': 'Lunch', 'calories': 50}).status_code == 401
    assert client.get('/api/day?date=2026-09-09').status_code == 401
    assert "frame-ancestors 'none'" in client.get('/').headers['content-security-policy']


def test_password_whitespace_is_preserved(client):
    payload = {'email': 'space@example.com', 'username': 'space', 'password': '  strong-password  '}
    assert client.post('/api/register', json=payload).status_code == 201
    client.post('/api/logout', json={})
    assert client.post('/api/login', json={'email': payload['email'], 'password': payload['password'].strip()}).status_code == 401
    assert client.post('/api/login', json={'email': payload['email'], 'password': payload['password']}).status_code == 200


def test_legacy_bcrypt_account_receives_goals(client, database):
    import bcrypt
    with database() as db:
        db.add(models.User(email='legacy@example.com', username='legacy',
                           hashed_password=bcrypt.hashpw(b'legacy-password', bcrypt.gensalt()).decode()))
        db.commit()
    assert client.post('/api/login', json={'email': 'legacy@example.com', 'password': 'legacy-password'}).status_code == 200
    assert client.get('/api/day?date=2026-09-09').json()['goals']['calories'] == 2000


def test_reject_invalid_account_and_goals(client):
    assert client.post('/api/register', json={'email': 'invalid', 'username': 'ok', 'password': 'strong-password'}).status_code == 422
    assert client.post('/api/register', json={'email': 'test@example.com', 'username': 'ok', 'password': 'short'}).status_code == 422
    register(client)
    assert client.put('/api/goals', json={'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}).status_code == 422
    assert client.get('/api/day?date=invalid').status_code == 422
