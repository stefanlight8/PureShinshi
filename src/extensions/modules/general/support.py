from crescent.commands import command
from crescent.context import Context
from miru.button import Button
from miru.view import View

from bot import Plugin

plugin = Plugin()


@plugin.include
@command(name="support", description="Сервер поддержки")
class Command:

    async def callback(self, context: Context) -> None:
        view: View = View()
        view.add_item(Button(label="Сервер поддержки", url=context.client.model.config['support_link']))

        await context.respond(
            components=view
        )
