from urllib.parse import urlparse

import pytest
from src.utils.installer_fetcher import (
    get_installer_url,
)
from src.utils.java_versions import get_java_version


def is_valid_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


@pytest.mark.asyncio
async def test_wrong_version_format():
    with pytest.raises(ValueError):
        await get_installer_url("neoforge", "1.21.beta")


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Neoforge maven probably died again.")
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


@pytest.mark.asyncio
async def test_installer_url_vanilla():
    url = await get_installer_url("vanilla", "1.21.1")
    assert is_valid_url(url)


def test_get_java_version():
    assert get_java_version("1.20") == 21
    assert get_java_version("1.19") == 17
    assert get_java_version("1.18") == 17
    assert get_java_version("1.17") == 16
    assert get_java_version("1.16") == 11
    assert get_java_version("1.15") == 11
    assert get_java_version("1.14") == 8
    assert get_java_version("1.12") == 8
    assert get_java_version("1.10.4") == 21
    with pytest.raises(ValueError):
        get_java_version("abd")
