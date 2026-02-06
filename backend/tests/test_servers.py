import pytest

# ---------------------------
# /health
# ---------------------------


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200


# ---------------------------
# GET /v1/servers
# ---------------------------


def test_list_servers_empty(client):
    response = client.get("/v1/servers")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------
# POST /v1/servers
# ---------------------------


@pytest.mark.parametrize(
    "loader,port",
    [
        ("forge", 25565),
        ("fabric", 25566),
        ("neoforge", 25567),
    ],
)
def test_create_server(client, loader, port):
    payload = {
        "name": "TestServer_" + loader,
        "mc_version": "1.20.1",
        "loader": loader,
        "port": port,
        "status": "stopped",
        "description": "vanilla",
        "xmx": 2048,
        "xms": 1024,
        "eula": True,
    }

    response = client.post("/v1/servers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestServer_" + loader
    assert data["port"] == port


def test_create_server_already_exists(client):
    payload = {
        "name": "TestServer_forge",
        "mc_version": "1.20.1",
        "loader": "forge",
        "port": 25565,
        "status": "stopped",
        "description": "vanilla",
        "xmx": 2048,
        "xms": 1024,
        "eula": True,
    }
    response = client.post("/v1/servers", json=payload)
    assert response.status_code == 400


def test_create_server_port_in_use(client):
    payload = {
        "name": "TestServer_forgee",
        "mc_version": "1.20.1",
        "loader": "forge",
        "port": 25565,
        "status": "stopped",
        "description": "vanilla",
        "xmx": 2048,
        "xms": 1024,
        "eula": True,
    }
    response = client.post("/v1/servers", json=payload)
    assert response.status_code == 400


def test_create_server_validation_error(client):
    payload = {
        "name": "InvalidServer",
        "mc_version": "1.20.1",
        "loader": "unknown_loader",
        "port": 25570,
        "status": "stopped",
        "description": "vanilla",
        "xmx": 2048,
        "xms": 1024,
        "eula": True,
    }

    response = client.post("/v1/servers", json=payload)
    assert response.status_code == 422


def test_create_server_jvm_arguments_error(client):
    payload = {
        "name": "JVMArgErrorServer",
        "mc_version": "1.20.1",
        "loader": "forge",
        "port": 25571,
        "status": "stopped",
        "description": "vanilla",
        "xmx": 1048,
        "xms": 2024,
        "eula": True,
        "jvm_arguments": "-Xmx2048M -Xms1024M -invalidArg",
    }

    response = client.post("/v1/servers", json=payload)
    assert response.status_code == 422


# ---------------------------
# GET /v1/servers/{server_id}
# ---------------------------


def test_server_not_found(client):
    response = client.get("/v1/servers/9999")
    assert response.status_code == 404


def test_get_server_success(client):
    response = client.get("/v1/servers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestServer_forge"
    assert data["port"] == 25565


# ---------------------------
# PATCH /v1/servers/{server_id}
# ---------------------------


def test_update_server_success(client):

    response = client.patch(
        "/v1/servers/1", json={"description": "Updated desc", "xmx": 2048}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated desc"
    assert response.json()["xmx"] == 2048


def test_update_server_validation_error(client):
    response = client.patch(
        "/v1/servers/1",
        json={"xmx": 999999},
    )
    assert response.status_code == 422


def test_update_server_ram_error(client):
    response = client.patch(
        "/v1/servers/1",
        json={"xmx": 1024, "xms": 2048},
    )
    assert response.status_code == 422


# ---------------------------
# DELETE /v1/servers/{server_id}
# ---------------------------


def test_delete_server_success(client):
    response = client.delete("/v1/servers/2")
    assert response.status_code == 200

    # Verify server is deleted
    get_response = client.get("/v1/servers/2")
    assert get_response.status_code == 404


def test_delete_server_not_found(client):
    response = client.delete("/v1/servers/999999")
    assert response.status_code in (404, 422)
