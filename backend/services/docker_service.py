import logging
from pathlib import Path

import docker
from utils.installer_fetcher import get_installer_url
from utils.java_versions import get_java_version

logger = logging.getLogger(__name__)


class DockerService:
    """Service for managing Docker containers for Minecraft servers"""

    _instance = None

    def __init__(self):
        self._client = None

    @classmethod
    def get_instance(cls) -> "DockerService":
        """Get singleton instance of DockerService"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_client(self):
        """Get or create Docker client"""
        if self._client is None:
            try:
                self._client = docker.from_env()
            except docker.errors.DockerException as e:
                logger.warning(f"Docker not available: {e}")
                raise
        return self._client

    async def start_server(
        self,
        server_name: str,
        mc_version: str,
        loader: str,
        port: int = 25565,
        xmx: int = 512,
        xms: int = 512,
        eula: bool = False,
    ):
        """Start a Minecraft server container"""
        try:
            logger.info(f"Starting server '{server_name}' (MC {mc_version}, {loader})")
            docker_client = self._get_client()
            container_name = f"mc-server-{server_name}"

            # Check if container exists
            try:
                container = docker_client.containers.get(container_name)
                if container.status == "running":
                    logger.info(f"Container already running: {container_name}")
                    return {"status": "running", "container_id": container.id}
                container.start()
                logger.info(f"Started container: {container_name}")
                return {"status": "running", "container_id": container.id}
            except docker.errors.NotFound:
                pass

            # Container doesn't exist - create new one
            logger.info(f"Creating new container for '{server_name}'")
            java_version = get_java_version(mc_version)
            server_jar = await get_installer_url(loader, mc_version)
            image_name = f"korniszon:mc-{server_name}"
            dockerfile_path = Path(__file__).parent / "Dockerfile.minecraft"

            logger.info(f"Building image: {image_name}")
            docker_client.images.build(
                path=str(dockerfile_path.parent),
                dockerfile="Dockerfile.minecraft",
                tag=image_name,
                buildargs={"JAVA_VERSION": str(java_version)},
                rm=True,
            )

            # Create volume if it doesn't exist
            volume_name = f"mc-server-{server_name}-data"
            try:
                docker_client.volumes.get(volume_name)
            except docker.errors.NotFound:
                docker_client.volumes.create(volume_name)

            # Start container
            container = docker_client.containers.run(
                image_name,
                detach=True,
                name=container_name,
                volumes=[f"{volume_name}:/server"],
                ports={"25565/tcp": port},
                environment={
                    "EULA": "true" if eula else "false",
                    "MC_VERSION": mc_version,
                    "LOADER": loader,
                    "SERVER_JAR": server_jar,
                    "XMX": str(int(xmx) if xmx else 512),
                    "XMS": str(int(xms) if xms else 512),
                },
            )
            logger.info(
                f"Server started: {server_name} (container: {container.id[:12]})"
            )
            return {"status": "running", "container_id": container.id}

        except Exception as e:
            logger.error(f"Failed to start server '{server_name}': {e}")
            return {"status": "error", "error": str(e)}

    async def stop_server(self, container_id: str):
        """Stop a running container"""
        try:
            docker_client = self._get_client()
            container = docker_client.containers.get(container_id)
            container.stop()
            logger.info(f"Stopped container {container_id}")
            return {"status": "stopped"}
        except Exception as e:
            logger.error(f"Failed to stop server: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def stop_and_remove_container(self, container_id: str):
        """Stop and remove a container"""
        try:
            docker_client = self._get_client()
            container = docker_client.containers.get(container_id)
            container.stop()
            container.remove()
            logger.info(f"Stopped and removed container {container_id}")
            return {"status": "removed"}
        except Exception as e:
            logger.error(f"Failed to stop and remove container: {str(e)}")
            return {"status": "error", "error": str(e)}


# Helper function for dependency injection
def get_docker_service() -> DockerService:
    """Get DockerService instance for FastAPI dependency injection"""
    return DockerService.get_instance()
