from crescent.commands import command, hook
from crescent.context import Context
from music.hooks import check_connection_hook
from music.join_function import join

from bot import Plugin

plugin = Plugin()


@plugin.include
@hook(check_connection_hook)
@command(name='join', description='Позвать меня в голосовой канал')
class Command:

    @staticmethod
    async def callback(context: Context) -> None:
        await join(context)
