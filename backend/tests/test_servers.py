import pytest


def test_list_servers_empty(client):
    response = client.get("/v1/servers")
    assert response.status_code == 200
    assert response.json() == []


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
