from typing import cast

from crescent.commands import command
from crescent.context import Context
from hikari.embeds import Embed
from hikari.impl import GatewayBot
from humanize.filesize import naturalsize
from psutil import Process

from bot import Plugin
from ext import embeds

plugin = Plugin()


@plugin.include
@command(name='about', description='Информация о боте на данный момент')
class Command:

    @staticmethod
    def get_status_emoji(config, latency: float) -> str:
        if latency > 200:
            return config['icons']['status']['middle']
        elif latency > 600:
            return config['icons']['status']['bad']
        else:
            return config['icons']['status']['good']

    async def callback(self, context: Context) -> None:
        process: Process = Process()
        bot: GatewayBot = cast(GatewayBot, context.app)
        config: dict = context.client.model.config
        users_count: int = sum(guild.member_count for guild in bot.cache.get_guilds_view().values())
        embed: Embed = embeds.default(
            title=f'Про {bot.get_me().username}',
            icon_url=config['icons']['about'],
            description=config['bot']['description']
        )
        embed.set_thumbnail(bot.get_me().avatar_url)
        embed.add_field(
            name='Основная информация',
            value='\n'.join([
                f"- Обслуживаем {len(bot.cache.get_guilds_view())} гильдий и {users_count} пользователей",
                f"- Используем {round(process.memory_percent(), 1)}% "
                f"({naturalsize(process.memory_full_info().uss)}) оперативной памяти",
                f"- {len(bot.voice.connections.keys())} голосовых подключений",
                f"- Я была запущена <t:{round(process.create_time())}:R>"
            ]),
            inline=True
        )
        latency: float = round(bot.heartbeat_latency * 1000, 2)
        embed.set_footer(
            text=f'Задержка: {latency}ms', icon=self.get_status_emoji(config, latency)
        )
        return await context.respond(embed=embed)
