from crescent.commands import command
from crescent.context import Context
from miru.button import Button
from miru.view import View

from bot import Plugin

plugin = Plugin()
SUPPORT_LINK = "https://discord.gg/3bXW7an2ke"


@plugin.include
@command(name="support", description="Сервер поддержки")
class Command:

    @staticmethod
    async def callback(context: Context) -> None:
        await context.respond(
            components=View().add_item(Button(label="Сервер поддержки", url=SUPPORT_LINK))
        )
