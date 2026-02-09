import logging
import re
import urllib.parse
import xml.etree.ElementTree as ElementTree

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def normalize_mc_version(mc_version: str) -> tuple[int, int, int]:
    parts = mc_version.split(".")
    if len(parts) == 2:
        parts.append("0")
    if len(parts) != 3 or parts[0] != "1":
        raise ValueError(f"Invalid Minecraft version format: {mc_version}")
    return tuple(map(int, parts))


def tuple_to_version(t: tuple[int, int, int]) -> str:
    return ".".join(map(str, t))


async def get_neoforge_url(
    client: httpx.AsyncClient, normalized: tuple[int, int, int]
) -> str | None:
    major, minor, patch = normalized

    resp = await client.get(
        "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"
    )
    try:
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.text)
    except (httpx.HTTPError, ElementTree.ParseError):
        logger.error(
            "Failed to fetch or parse NeoForge metadata for version {normalized}."
        )
        return None

    versions = [v.text for v in root.findall(".//version")]
    matching = [v for v in versions if v.startswith(f"{minor}.{patch}.")]

    if not matching:
        return None

    def normalize(v: str) -> str:
        return v.split("-")[0]

    stable = [v for v in matching if "-beta" not in v]
    if stable:
        latest = sorted(stable, key=lambda x: list(map(int, normalize(x).split("."))))[
            -1
        ]
    else:
        latest = sorted(
            matching, key=lambda x: list(map(int, normalize(x).split(".")))
        )[-1]

    latest_norm = normalize(latest)

    return (
        f"https://maven.neoforged.net/releases/net/neoforged/neoforge/"
        f"{latest_norm}/neoforge-{latest_norm}-installer.jar"
    )


async def get_fabric_url(
    client: httpx.AsyncClient, normalized: tuple[int, int, int]
) -> str | None:
    resp = await client.get(
        "https://maven.fabricmc.net/net/fabricmc/fabric-installer/maven-metadata.xml"
    )
    resp.raise_for_status()
    root = ElementTree.fromstring(resp.text)

    latest = root.findtext(".//latest")
    if not latest:
        return None

    return (
        f"https://maven.fabricmc.net/net/fabricmc/fabric-installer/"
        f"{latest}/fabric-installer-{latest}.jar"
    )


async def get_forge_url(
    client: httpx.AsyncClient, normalized: tuple[int, int, int]
) -> str | None:
    mc_version = tuple_to_version(normalized)
    page_url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{mc_version}.html"

    resp = await client.get(page_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    link_tag = soup.find("a", title="Installer")
    if not link_tag:
        return None

    raw_href = link_tag.get("href")
    if not raw_href:
        return None

    parsed = urllib.parse.urlparse(raw_href)
    qs = urllib.parse.parse_qs(parsed.query)
    return qs.get("url", [None])[0]


async def get_vanilla_url(
    client: httpx.AsyncClient, normalized: tuple[int, int, int]
) -> str | None:
    mc_version = tuple_to_version(normalized)

    manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
    resp = await client.get(manifest_url)
    resp.raise_for_status()
    manifest = resp.json()

    entry = next((v for v in manifest["versions"] if v["id"] == mc_version), None)
    if not entry:
        logger.warning(f"Vanilla version {mc_version} not found in Mojang manifest.")
        return None

    version_manifest_url = entry["url"]
    resp = await client.get(version_manifest_url)
    resp.raise_for_status()
    version_manifest = resp.json()

    try:
        return version_manifest["downloads"]["server"]["url"]
    except KeyError:
        logger.error(f"No server.jar found for vanilla version {mc_version}.")
        return None


ENGINES = {
    "neoforge": get_neoforge_url,
    "fabric": get_fabric_url,
    "forge": get_forge_url,
    "vanilla": get_vanilla_url,
}


async def get_installer_url(engine: str, mc_version: str) -> str | None:
    """
    Get the installer URL for a given Minecraft version and engine.
    """

    if not re.match(r"^\d+\.\d+(\.\d+)?$", mc_version):
        raise ValueError(f"Invalid Minecraft version format: {mc_version}")

    normalized = normalize_mc_version(mc_version)

    engine = engine.lower()
    if engine not in ENGINES:
        raise ValueError(f"Unknown engine: {engine}")

    async with httpx.AsyncClient() as client:
        return await ENGINES[engine](client, normalized)
