from crescent.commands import command, option, HookResult, hook
from crescent.context import Context
from hikari import User

from bot import Plugin
from ext import WaifuPicsAdapter, embeds

plugin = Plugin()


async def check_hook(context: Context) -> HookResult:
    target: User = context.options['user']

    if context.member.user == target:
        await context.respond(embed=embeds.error('Вы не можете дать подзатыльник самому себе'), ephemeral=True)
        return HookResult(exit=True)

    if target.is_bot:
        await context.respond(embed=embeds.error('Вы не можете дать подзатыльник боту'), ephemeral=True)
        return HookResult(exit=True)

    else:
        return HookResult(exit=False)


@plugin.include
@hook(check_hook)
@command(name="bonk", description="Подзатыльник 😡", dm_enabled=False)
class Command:
    user: User = option(User, description="Кого вы хотите ударить")
    message: str = option(str, description="Сказать что-нибудь", max_length=200, default=None)

    async def callback(self, context: Context) -> None:
        api: WaifuPicsAdapter = WaifuPicsAdapter()
        target: User = self.user

        await context.respond(
            embed=embeds.default(
                title=f'{context.member.username} дал(а) подзатыльник {target.username}',
                icon_url=context.member.display_avatar_url.url,
                description=self.message
            ).set_image(await api.get_gif('bonk'))
        )