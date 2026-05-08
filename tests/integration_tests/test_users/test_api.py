# def test_abc():
#     assert 1 == 1


import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("email, password, status_code", [
    ("kot@pes.com", "kotopes", 200),
    ("kot@pes.com", "kotopes", 409),
    ("pes@kot.com", "kotopes", 200),
    ("abcde", "kotopes", 422)
])
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/register", json={
        "email": email,
        "password":  password,
    })

    assert response.status_code == status_code


@pytest.mark.parametrize("email, password, status_code", {
    ("test@test.com", "test", 200),
    ("admin@test.com", "admin", 200)
})
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/login", json={
        "email": email,
        "password": password,
    })

    assert response.status_code == status_code