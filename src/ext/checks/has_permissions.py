from typing import Callable, Awaitable

from crescent import HookResult, Context
from hikari import Permissions, InteractionMember, GatewayBot

from .localized_permissions import LOCALIZED_PERMISSIONS
from ..embeds import error

__all__ = ['has_permissions']


def has_permissions(
        permissions: Permissions,
) -> Callable[[Context], Awaitable[HookResult | None]]:
    async def check(ctx: Context) -> HookResult | None:
        member = ctx.member
        assert isinstance(member, InteractionMember)
        assert isinstance(ctx.app, GatewayBot)
        guild = ctx.app.cache.get_guild(ctx.guild_id)
        assert guild is not None
        if permissions not in member.permissions:
            await ctx.respond(
                embed=error(
                    'У вас недостаточно прав для выполнения команды',
                    'Вам не хватает таких прав, как:\n'
                    '\n'.join(f"⎯ {LOCALIZED_PERMISSIONS[permission]}" for permission in permissions)
                ),
                ephemeral=True
            )
            return HookResult(True)
        return None

    return check
