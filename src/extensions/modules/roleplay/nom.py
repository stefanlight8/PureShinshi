from typing import cast

from crescent.commands import command, option, HookResult, hook
from crescent.context import Context
from hikari import User
from hikari.impl import GatewayBot

from bot import Plugin
from ext import WaifuPicsAdapter, embeds

plugin = Plugin()


async def check_hook(context: Context) -> HookResult:
    bot: GatewayBot = cast(GatewayBot, context.app)
    target: User = context.options['user']

    if context.member.id == target.id:
        await context.respond(
            embed=embeds.error(
                'Таким образом не получится',
                'Вы просто можете проигнорировать аргумент `member` и вы покушаете самостоятельно'
            )
        )
        return HookResult(exit=True)

    if target.is_bot:
        if target.id == bot.get_me().id:
            return HookResult(exit=False)
        else:
            await context.respond(
                embed=embeds.error("Других ботов покормить не получится, а я не откажусь"),
                ephemeral=True
            )
            return HookResult(exit=True)

    else:
        return HookResult(exit=False)


@plugin.include
@hook(check_hook)
@command(name="nom", description="Покормить", dm_enabled=False)
class Command:
    user: User | None = option(User, description="Кого вы хотите покормить", default=None)
    message: str = option(str, description="Сказать что-нибудь", max_length=200, default=None)

    async def callback(self, context: Context) -> None:
        api: WaifuPicsAdapter = WaifuPicsAdapter()
        target: User = self.user
        session = context.client.model.session

        if self.user:
            await context.respond(
                embed=embeds.default(
                    title=f'{context.member.username} покормил {target.username}',
                    icon_url=context.member.display_avatar_url.url,
                    description=self.message
                ).set_image(await api.get_gif(session, 'nom'))
            )
        else:
            await context.respond(
                embed=embeds.default(
                    title=f'{context.member.username} кушает',
                    icon_url=context.member.default_avatar_url.url,
                    description=self.message
                ).set_image(await api.get_gif('nom'))
            )
