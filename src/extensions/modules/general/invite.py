from typing import cast

from crescent.commands import command
from crescent.context import Context
from hikari import GatewayBot
from miru import Button, View
from yarl import URL

from bot import Plugin

plugin = Plugin()


def create_discord_auth_link(client_id: int | str, scope: list, permissions: int) -> str:
    base_url = "https://discord.com/oauth2/authorize"
    query_params = {
        "client_id": client_id,
        "scope": ' '.join(scope),
        "permissions": permissions
    }
    url = URL(base_url).with_query(query_params)
    return str(url)


@plugin.include
@command(name="invite", description="Пригласить бота")
class Command:

    async def callback(self, context: Context) -> None:  # type: ignore
        bot: GatewayBot = cast(GatewayBot, context.app)
        view: View = View()

        view.add_item(
            Button(
                label="С правами администратора",
                url=create_discord_auth_link(bot.get_me().id, ['bot', 'applications.commands'], 8),
            )
        )
        view.add_item(
            Button(
                label="Без прав",
                url=create_discord_auth_link(bot.get_me().id, ['bot', 'applications.commands'], 0),
            )
        )

        await context.respond(
            components=view
        )
