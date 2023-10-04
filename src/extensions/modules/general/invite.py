from typing import cast

from crescent.commands import command
from crescent.context import Context
from hikari.impl import GatewayBot
from miru.button import Button
from miru.view import View

from bot import Plugin

plugin = Plugin()
INVITE_LINK: str = ("https://discord.com/oauth2/authorize"
                    "?client_id={client_id}&scope={scopes}&permissions={permissions}")


@plugin.include
@command(name="invite", description="Пригласить бота")
class Command:

    @staticmethod
    async def callback(context: Context) -> None:
        bot: GatewayBot = cast(GatewayBot, context.app)
        view: View = View()

        view.add_item(
            Button(
                label="С правами администратора",
                url=INVITE_LINK.format(
                    client_id=bot.get_me().id, scopes="bot+applications.commands", permissions=8
                ),
            )
        )
        view.add_item(
            Button(
                label="Без прав",
                url=INVITE_LINK.format(
                    client_id=bot.get_me().id, scopes="bot+applications.commands", permissions=0
                ),
            )
        )

        await context.respond(
            components=view
        )
