from urllib.parse import urlparse

import httpx
import pytest
from src.utils.installer_fetcher import (
    get_fabric_url,
    get_forge_url,
    get_installer_url,
    get_neoforge_url,
)


def is_valid_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


@pytest.mark.asyncio
async def test_neoforge_real():
    async with httpx.AsyncClient() as client:
        url = await get_neoforge_url(client, (1, 21, 1))
    assert is_valid_url(url)


@pytest.mark.asyncio
async def test_fabric_real():
    async with httpx.AsyncClient() as client:
        url = await get_fabric_url(client, (1, 21, 1))
    assert is_valid_url(url)


@pytest.mark.asyncio
async def test_forge_real():
    async with httpx.AsyncClient() as client:
        url = await get_forge_url(client, (1, 21, 1))
    assert url is None or is_valid_url(url)


@pytest.mark.asyncio
async def test_wrong_version_format():
    with pytest.raises(ValueError):
        await get_installer_url("neoforge", "1.21.beta")


@pytest.mark.asyncio
async def test_installer_url_neoforge():
    url = await get_installer_url("neoforge", "1.21.1")
    assert is_valid_url(url)


@pytest.mark.asyncio
async def test_installer_url_fabric():
    url = await get_installer_url("fabric", "1.21.1")
    assert is_valid_url(url)


@pytest.mark.asyncio
async def test_installer_url_forge():
    url = await get_installer_url("forge", "1.21.1")
    assert url is None or is_valid_url(url)
