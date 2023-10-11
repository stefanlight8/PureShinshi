from datetime import timedelta
from typing import cast

from crescent.commands import Group, command, option, hook
from crescent.context import Context
from crescent.ext.cooldowns import cooldown
from hikari import GatewayBot, Embed, User, Member
from miru import Button, View

from bot import Plugin, BotModel
from ext import embeds

plugin = Plugin()
group = Group('user', dm_enabled=False)


@plugin.include
@group.child
@hook(cooldown(1, timedelta(seconds=10)))
@command(name="info", description="Получить информацию о пользователе или о себе")
class Command:
    target: User = option(User, description='Укажите пользователя или его ID', default=None)

    async def callback(self, context: Context) -> None:
        client: BotModel = context.client.model
        view: View = View()

        if not self.target:
            user = context.member
        else:
            user = self.target

        icon_of = client.config['icons']['user']

        embed: Embed = embeds.default(
            title=user.global_name if user.global_name else user.username,
            description=f'@{user.username}' if user.global_name else None,
            icon_url=icon_of['bot'] if user.is_bot else icon_of['member'],
            colour=user.accent_color
        )
        embed.set_thumbnail(user.display_avatar_url.url)
        embed.set_footer(text=f"ID: {str(user.id)}")
        embed.add_field(
            name='Создан',
            value=f"<t:{round(user.created_at.timestamp())}:R>\n"
                  f"(<t:{round(user.created_at.timestamp())}:D>)",
            inline=True
        )

        if isinstance(self.target, Member) or not self.target:
            if self.target:
                member: Member = self.target
            else:
                member: Member = context.member

            embed.add_field(
                name=f'Зашел на {context.guild.name}',
                value=f"<t:{round(user.joined_at.timestamp())}:R>\n"
                      f"(<t:{round(user.joined_at.timestamp())}:D>)",
                inline=True
            )

            roles = [
                        role.mention for role in sorted(member.get_roles(), key=lambda role: role.position)
                        if role.name != "@everyone"
                    ][::-1]

            if not roles:
                embed.add_field(name="Роли", value="Нет", inline=False)
            else:
                if len(roles) > 5:
                    embed.add_field(
                        name="Роли",
                        value="{}... и {} других ролей".format(
                            ", ".join(roles[:5]), (len(roles) - 5)
                        ),
                        inline=False,
                    )
                else:
                    embed.add_field(name="Роли", value=", ".join(roles), inline=False)

        await context.respond(
            embed=embed,
            components=view
        )


@plugin.include
@group.child
@hook(cooldown(1, timedelta(seconds=10)))
@command(name="avatar", description="Получить свой аватар или пользователя")
class Command:
    target: User = option(User, description="Кого аватарку вы хотите получить", default=None)

    async def callback(self, context: Context) -> None:
        view: View = View()

        if not self.target:
            user = context.member
        else:
            user = self.target

        if user.avatar_hash:
            avatar_url: str = user.avatar_url.url

            view.add_item(Button(label="256x256", url=user.make_avatar_url(size=256).url))
            view.add_item(Button(label="512x512", url=user.make_avatar_url(size=512).url))
            view.add_item(Button(label="1024x1024", url=user.make_avatar_url(size=1024).url))
        else:
            avatar_url: str = user.display_avatar_url.url
            view.add_item(Button(label="Ссылка", url=avatar_url))

        await context.respond(
            embed=embeds.default(
                title=f'Аватар {user.username}'
            ).set_image(avatar_url),
            components=view
        )


@plugin.include
@group.child
@hook(cooldown(1, timedelta(seconds=10)))
@command(name="banner", description="Получить свой баннер или пользователя")
class Command:
    target: User = option(User, description="Кого баннер вы хотите получить", default=None)

    async def callback(self, context: Context) -> None:
        bot: GatewayBot = cast(GatewayBot, context.app)
        view: View = View()

        if not self.target:
            user = context.member
            no_banner_embed = embeds.error('У вас нет баннера')
        else:
            user = self.target
            no_banner_embed = embeds.error('У данного пользователя нет баннера')

        user = await bot.rest.fetch_user(user)

        if user.banner_hash:
            banner_url: str = user.banner_url.url

            view.add_item(Button(label="512", url=user.make_banner_url(size=512).url))
            view.add_item(Button(label="1024", url=user.make_banner_url(size=1024).url))
            view.add_item(Button(label="2048", url=user.make_banner_url(size=2048).url))
        else:
            return await context.respond(embed=no_banner_embed, ephemeral=True)

        await context.respond(
            embed=embeds.default(
                title=f'Баннер {user.username}',
                icon_url=user.display_avatar_url.url
            ).set_image(banner_url),
            components=view
        )
