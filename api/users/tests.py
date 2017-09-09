from .models import User
from apistar.test import TestClient
from apistar.backends.sqlalchemy_backend import Session


def test_users_list_empty(session: Session, client: TestClient):
    response = client.get('/users/')
    assert response.status_code == 200
    assert response.json() == []


def test_users_list(session: Session, client: TestClient):
    user = User(first_name='asdf', last_name='Easdf')
    session.add(user)
    session.commit()

    user2 = User(first_name='asdf2', last_name='Easdf44')
    session.add(user2)
    session.commit()

    response = client.get('/users/')
    assert response.status_code == 200
    assert response.json() == [{
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name
    }, {
        "id": user2.id,
        "first_name": user2.first_name,
        "last_name": user2.last_name
    }]


def test_user_create(session: Session, client: TestClient):
    response = client.post('/users/', data={
        "first_name": "user 7776776",
        "last_name": "dfrfrfrf6"
    })

    user = session.query(User).filter(
        User.first_name == "user 7776776"
    ).order_by(User.id.desc()).first()

    assert response.status_code == 201
    assert response.json() == {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name
    }


def test_user_view(session: Session, client: TestClient):
    user = User(first_name='asdf34534', last_name='sdkfisdfk')
    session.add(user)
    session.commit()

    response = client.get('/users/{}'.format(user.id))
    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name
    }


def test_user_delete(session: Session, client: TestClient):
    user = User(first_name='asdf45455g45', last_name='sdkfis444r4')
    session.add(user)
    session.commit()

    query = session.query(User).filter(
        User.id == user.id
    )
    assert query.count() == 1

    response = client.delete('/users/{}'.format(user.id))

    assert response.status_code == 204
    assert response.text == ""
    assert query.count() == 0


def test_user_update(session: Session, client: TestClient):
    user = User(first_name='asdf445454', last_name='sdkfis4555')
    session.add(user)
    session.commit()

    response = client.patch('/users/{}'.format(user.id), data={
        "first_name": "user's new name",
        "last_name": "user's new last name"
    })

    session.refresh(user)
    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "first_name": "user's new name",
        "last_name": user.last_name
    }
    assert user.first_name == "user's new name"


def test_user_not_exists(client: TestClient):
    res = client.get('/users/8884444')
    res1 = client.patch('/users/8884444')
    res2 = client.delete('/users/8884444')

    assert res.status_code == res1.status_code == res2.status_code == 404
    assert res.json() == res1.json() == res2.json() == {"message": "Not found"}
