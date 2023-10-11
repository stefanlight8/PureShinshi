from datetime import timedelta

from crescent.commands import HookResult, command, option, hook
from crescent.context import Context
from crescent.ext.cooldowns import cooldown
from hikari import User

from bot import Plugin
from ext import WaifuPicsAdapter, embeds

plugin = Plugin()


async def check_hook(context: Context) -> HookResult:
    target: User = context.options['user']

    if context.member.id == target.id:
        await context.respond(embed=embeds.error('Вы не можете лизнуть самого себя'), ephemeral=True)
        return HookResult(exit=True)

    if target.is_bot:
        await context.respond(embed=embeds.error('Вы не можете лизнуть бота'), ephemeral=True)
        return HookResult(exit=True)

    else:
        return HookResult(exit=False)


@plugin.include
@hook(check_hook)
@hook(cooldown(3, timedelta(seconds=10)))
@command(name="lick", description="лизнуть", dm_enabled=False)
class Command:
    user: User = option(User, description="Кого вы хотите лизнуть")
    message: str = option(str, description="Сказать что-нибудь", max_length=200, default=None)

    async def callback(self, context: Context) -> None:
        api: WaifuPicsAdapter = WaifuPicsAdapter()
        target: User = self.user
        session = context.client.model.session

        await context.respond(
            embed=embeds.default(
                title=f'{context.member.username} лизнул {target.username}',
                icon_url=context.member.display_avatar_url.url,
                description=self.message
            ).set_image(await api.get_gif(session, 'lick'))
        )
