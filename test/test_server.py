async def test_client(client):
    resp = await client.get("/")
    assert resp.status == 200
