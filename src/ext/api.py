from aiohttp import ClientSession


class RequestError(Exception):
    ...


class Request:

    @staticmethod
    async def text(*args, **kwargs) -> str:
        async with ClientSession() as session:
            async with session.request(*args, **kwargs) as response:
                if response.status in (200, 201):
                    return await response.text()
                raise RequestError(
                    f"Something wrong, response status is {response.status}"
                )

    @staticmethod
    async def json(*args, **kwargs) -> dict:
        async with ClientSession() as session:
            async with session.request(*args, **kwargs) as response:
                if response.status in (200, 201):
                    return await response.json()
                raise RequestError(
                    f"Something wrong, response status is {response.status}"
                )


class WaifuPicsAdapter:
    def __init__(self) -> None:
        self.base_url = "https://api.waifu.pics/sfw"

    async def get_gif(self, endpoint: str) -> str:
        response = await Request.json("GET", f"{self.base_url}/{endpoint}")
        return response["url"]


__all__ = ['Request', 'WaifuPicsAdapter']
