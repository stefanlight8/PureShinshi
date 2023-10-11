from datetime import timedelta
from os import getenv

from aiohttp import ClientSession
from crescent import command, hook, Context, option
from crescent.ext.cooldowns import cooldown
from yarl import URL

from bot import BotModel, Plugin
from ext import embeds

plugin = Plugin()


@plugin.include
@hook(cooldown(1, timedelta(seconds=15)))
@command(name='weather', description='Узнать погоду')
class Command:
    place = option(
        str,
        description='Пример: Германия, Берлин; или просто название страны/города',
        max_length=50
    )

    async def callback(self, context: Context) -> None:
        client: BotModel = context.client.model
        session: ClientSession = client.session

        await context.defer()
        async with session.request(
                'GET',
                URL("https://api.openweathermap.org/data/2.5/weather").with_query({
                    'q': self.place,
                    'appid': getenv('OWM_API_KEY'),
                    'lang': 'ru',
                    'units': 'metric'
                })
        ) as response:
            if response.status not in (200, 201):
                return await context.respond(
                    embed=embeds.error(
                        "Ошибка API", "По всей видимости такого города/ страны нет"
                    )
                )
            else:
                response = await response.json()

            icon = client.config["icons"]["weather"][response["weather"][0]["icon"]]
            place = f"{response['sys']['country']}, {response['name']}"

            embed = embeds.default(
                title=f"Погода в {place}",
                icon_url=client.config["icons"]["about"],
                description=response["weather"][0]["description"].title(),
            )
            embed.set_thumbnail(icon)
            embed.set_footer(text="Powered by OpenWeatherAPI")

            embed.add_field(
                name=f"Температура: {response['main']['temp']}°C",
                value=f"Чувствуется как: {response['main']['feels_like']}°C",
                inline=True
            )
            embed.add_field(
                name=f"Влажность: {response['main']['humidity']}%",
                value=f"Давление: {response['main']['pressure']} hPa",
                inline=True
            )
            embed.add_field(
                name="Ветер",
                value=f"Скорость: `{response['wind']['speed']} км/ч`\n"
                      f"Направление: `{response['wind']['deg']}°`",
                inline=False
            )
            embed.add_field(name="Облачность", value=f"{response['clouds']['all']}%", inline=True)

            return await context.respond(embed=embed)
