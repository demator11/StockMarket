import time

import pytest


@pytest.mark.parametrize(
    "name,expected_status",
    [
        ("User1", 200),
        ("User2", 200),
        ("User2", 409),
        ("U2", 422),
    ],
)
def test_register_user(client, name, expected_status):
    time.sleep(0.5)
    response = client.post("api/v1/public/register", json={"name": name})
    assert response.status_code == expected_status


# @pytest.mark.asyncio
# async def test_register_user2():
#     async with AsyncClient(
#         transport=ASGITransport(app), base_url="http://test"
#     ) as client:
#         response = await client.post(
#             "api/v1/public/register", json={"name": "User2"}
#         )
#         assert response.status_code == 200
