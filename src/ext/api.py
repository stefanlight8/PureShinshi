__all__ = ['WaifuPicsAdapter']


class WaifuPicsAdapter:
    BASE_URL = "https://api.waifu.pics/sfw"

    async def get_gif(self, session, endpoint: str) -> str:
        async with session.request('GET', f'{self.BASE_URL}/{endpoint}') as response:
            response = await response.json()
        return response["url"]
