from unittest.mock import AsyncMock, MagicMock, patch

import docker
import pytest
from src.services.docker_service import DockerService

# ---------------------------
# FIXTURES
# ---------------------------


@pytest.fixture
def docker_service():
    DockerService._instance = None
    return DockerService.get_instance()


# ---------------------------
# DockerService: start_server()
# ---------------------------


@pytest.mark.asyncio
@patch("src.services.docker_service.get_installer_url", new_callable=AsyncMock)
@patch("src.services.docker_service.get_java_version")
@patch("src.services.docker_service.docker.from_env")
async def test_start_server_creates_new_container(
    mock_from_env, mock_java_version, mock_installer_url, docker_service
):
    mock_java_version.return_value = 17
    mock_installer_url.return_value = "https://example.com/server.jar"

    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    mock_client.containers.get.side_effect = docker.errors.NotFound("not found")
    mock_client.images.build.return_value = ("image", [])
    mock_client.volumes.get.side_effect = docker.errors.NotFound("not found")
    mock_client.volumes.create.return_value = MagicMock()

    fake_container = MagicMock()
    fake_container.id = "abc123"
    mock_client.containers.run.return_value = fake_container

    result = await docker_service.start_server(
        server_name="test",
        mc_version="1.20.1",
        loader="fabric",
        port=25565,
        xmx=1024,
        xms=1024,
        eula=True,
    )

    assert result["status"] == "running"
    assert result["container_id"] == "abc123"


@pytest.mark.asyncio
@patch("src.services.docker_service.docker.from_env")
async def test_start_server_existing_running_container(mock_from_env, docker_service):
    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    fake_container = MagicMock()
    fake_container.status = "running"
    fake_container.id = "xyz789"

    mock_client.containers.get.return_value = fake_container

    result = await docker_service.start_server("test", "1.20.1", "fabric")

    assert result["status"] == "running"
    assert result["container_id"] == "xyz789"
    fake_container.start.assert_not_called()


@pytest.mark.asyncio
@patch("src.services.docker_service.docker.from_env")
async def test_start_server_existing_stopped_container(mock_from_env, docker_service):
    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    fake_container = MagicMock()
    fake_container.status = "exited"
    fake_container.id = "zzz111"

    mock_client.containers.get.return_value = fake_container

    result = await docker_service.start_server("test", "1.20.1", "fabric")

    fake_container.start.assert_called_once()
    assert result["status"] == "running"
    assert result["container_id"] == "zzz111"


# ---------------------------
# DockerService: stop_server()
# ---------------------------


@pytest.mark.asyncio
@patch("src.services.docker_service.docker.from_env")
async def test_stop_server_success(mock_from_env, docker_service):
    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    fake_container = MagicMock()
    mock_client.containers.get.return_value = fake_container

    result = await docker_service.stop_server("abc123")

    fake_container.stop.assert_called_once()
    assert result["status"] == "stopped"


@pytest.mark.asyncio
@patch("src.services.docker_service.docker.from_env")
async def test_stop_server_error(mock_from_env, docker_service):
    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    mock_client.containers.get.side_effect = Exception("boom")

    result = await docker_service.stop_server("abc123")

    assert result["status"] == "error"
    assert "boom" in result["error"]


# ---------------------------
# DockerService: restart_server()
# ---------------------------


@pytest.mark.asyncio
@patch("src.services.docker_service.docker.from_env")
async def test_restart_server_success(mock_from_env, docker_service):
    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    fake_container = MagicMock()
    mock_client.containers.get.return_value = fake_container

    result = await docker_service.restart_server("abc123")

    fake_container.restart.assert_called_once()
    assert result["status"] == "restarted"


@pytest.mark.asyncio
@patch("src.services.docker_service.docker.from_env")
async def test_restart_server_not_found(mock_from_env, docker_service):
    mock_client = MagicMock()
    mock_from_env.return_value = mock_client

    mock_client.containers.get.side_effect = Exception("NotFound")

    result = await docker_service.restart_server("abc123")

    assert result["status"] == "error"
