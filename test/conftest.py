import pytest

from missbot import app_factory


@pytest.fixture
async def server(aiohttp_server):
    return await aiohttp_server(await app_factory())


@pytest.fixture
async def client(aiohttp_client, server):
    return await aiohttp_client(server)
