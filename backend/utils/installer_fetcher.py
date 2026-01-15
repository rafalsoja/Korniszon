import re
import urllib.parse
import xml.etree.ElementTree as ET

import httpx
from bs4 import BeautifulSoup


def normalize_mc_version(mc_version: str) -> tuple[int, int, int]:
    parts = mc_version.split(".")
    if len(parts) == 2:
        parts.append("0")
    if len(parts) != 3 or parts[0] != "1":
        raise ValueError(f"Invalid Minecraft version format: {mc_version}")
    return tuple(map(int, parts))


async def get_neoforge_url(client: httpx.AsyncClient, mc_version: str) -> str | None:
    major, minor, patch = normalize_mc_version(mc_version)

    resp = await client.get(
        "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    versions = [v.text for v in root.findall(".//version")]
    # NeoForge versioning: MC 1.21.1 -> NeoForge 21.1.X
    matching = [v for v in versions if v.startswith(f"{minor}.{patch}.")]

    if not matching:
        return None

    def normalize(v: str) -> str:
        return v.split("-")[0]

    # Try to find stable version first
    stable = [v for v in matching if "-beta" not in v]
    if stable:
        latest = sorted(stable, key=lambda x: list(map(int, normalize(x).split("."))))[
            -1
        ]
    else:
        # If no stable version, use beta
        latest = sorted(
            matching, key=lambda x: list(map(int, normalize(x).split(".")))
        )[-1]

    latest_norm = normalize(latest)

    return (
        f"https://maven.neoforged.net/releases/net/neoforged/neoforge/"
        f"{latest_norm}/neoforge-{latest_norm}-installer.jar"
    )


async def get_fabric_url(client: httpx.AsyncClient, mc_version: str) -> str | None:
    resp = await client.get(
        "https://maven.fabricmc.net/net/fabricmc/fabric-installer/maven-metadata.xml"
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    latest = root.findtext(".//latest")
    if not latest:
        return None

    return (
        f"https://maven.fabricmc.net/net/fabricmc/fabric-installer/"
        f"{latest}/fabric-installer-{latest}.jar"
    )


async def get_forge_url(client: httpx.AsyncClient, mc_version: str) -> str | None:
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


ENGINES = {
    "neoforge": get_neoforge_url,
    "fabric": get_fabric_url,
    "forge": get_forge_url,
}


async def get_installer_url(engine: str, mc_version: str) -> str | None:
    """
    Get the installer URL for a given Minecraft version and engine.
    """
    if not re.match(r"^\d+\.\d+(\.\d+)?$", mc_version):
        raise ValueError(f"Invalid Minecraft version format: {mc_version}")

    engine = engine.lower()
    if engine not in ENGINES:
        raise ValueError(f"Unknown engine: {engine}")

    async with httpx.AsyncClient() as client:
        return await ENGINES[engine](client, mc_version)
