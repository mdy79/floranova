import pytest


@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    # 1. Register new user
    register_payload = {
        "email": "newuser@test.ir",
        "full_name": "سروش یوسفی",
        "password": "Password123!",
        "phone_number": "09129998877",
    }
    resp = await client.post("/api/v1/auth/register", json=register_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@test.ir"
    assert data["role"] == "CUSTOMER"

    # 2. Login
    login_payload = {
        "email": "newuser@test.ir",
        "password": "Password123!",
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Fetch profile
    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "newuser@test.ir"


@pytest.mark.asyncio
async def test_duplicate_email_registration_rejected(client):
    payload = {
        "email": "admin@test.ir",
        "full_name": "مدیر تکراری",
        "password": "Password123!",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400
    assert "قبلاً" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_login_credentials(client):
    payload = {
        "email": "admin@test.ir",
        "password": "WrongPassword!",
    }
    resp = await client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 401
