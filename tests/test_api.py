def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_login_and_me(auth_client):
    assert auth_client.get("/auth/me").json()["email"] == "test@example.com"


def test_duplicate_register(client):
    body = {"email": "a@example.com", "password": "password123"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 400


def test_wrong_password(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "password123"})
    r = client.post("/auth/login", data={"username": "a@example.com", "password": "nope-nope"})
    assert r.status_code == 401


def test_protected_needs_login(client):
    assert client.get("/paychecks").status_code == 401


def test_preview_split(client):
    r = client.post("/split", json={"amount": 1500})
    assert r.json()["savings"] == "300.00"


def test_paycheck_history_and_savings(auth_client):
    auth_client.post("/paychecks", json={"amount": 1000, "paid_on": "2026-08-01"})
    auth_client.post("/paychecks", json={"amount": 1000, "paid_on": "2026-09-01"})
    history = auth_client.get("/paychecks").json()
    assert len(history) == 2 and history[0]["tip"]

    r = auth_client.get("/savings/target", params={"actual": 300}).json()
    assert r["target_savings"] == "400.00"
    assert r["difference"] == "-100.00"
    assert "behind" in r["commentary"]


def test_cannot_delete_other_users_paycheck(auth_client, client):
    pc = auth_client.post("/paychecks", json={"amount": 500}).json()
    client.post("/auth/register", json={"email": "b@example.com", "password": "password123"})
    tok = client.post("/auth/login", data={"username": "b@example.com", "password": "password123"}).json()["access_token"]
    r = client.delete(f"/paychecks/{pc['id']}", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 404


def test_stock_instruments_sample(auth_client):
    items = auth_client.get("/stocks/instruments", params={"q": "vanguard"}).json()
    assert len(items) == 2
