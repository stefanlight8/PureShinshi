from datetime import timedelta
from re import compile
from typing import cast

from crescent.commands import command, option, hook
from crescent.context import Context
from crescent.ext.cooldowns import cooldown
from hikari.embeds import Embed
from hikari.errors import (
    UnauthorizedError, NotFoundError, RateLimitTooLongError, InternalServerError
)
from hikari.impl import GatewayBot
from hikari.users import User
from miru import View
from miru.button import Button

from bot import Plugin, BotModel
from ext import embeds

plugin = Plugin()


@plugin.include
@hook(cooldown(1, period=timedelta(seconds=10)))
@command(name="whois", description="Получить информацию о пользователе через ID")
class Command:
    user_id = option(str, name='id', description='ID пользователя, о котором хотите получить информацию')

    async def callback(self, context: Context) -> None:
        if not bool(compile(r"^[0-9]+$").match(self.user_id)):
            return await context.respond(
                embed=embeds.error(
                    "Ошибка аргументов",
                    description="ID является невалидным или в нем есть буквы.\n"
                )
            )

        user_id: int = int(self.user_id)
        bot: GatewayBot = cast(GatewayBot, context.app)
        client: BotModel = context.client.model
        view: View = View()

        user_in_cache: User | None = bot.cache.get_user(user_id)

        if user_in_cache:
            user: User = user_in_cache
        else:
            try:
                user: User = await bot.rest.fetch_user(user_id)
            except UnauthorizedError:
                return await context.respond(
                    embed=embeds.error(
                        'Внутренняя ошибка',
                        description='Бот не авторизирован в Discord API, обратитесь в поддержку.'
                    )
                )
            except NotFoundError:
                return await context.respond(
                    embed=embeds.error(
                        'Пользователь не был найден',
                        description='Попробуйте изменить ID'
                    )
                )
            except RateLimitTooLongError:
                return await context.respond(
                    embed=embeds.error(
                        'Слишком долгое ожидание ответа',
                        description='Мы устали ждать, так что пользователя не удалось получить.\n'
                                    'Попробуйте изменить ID.'
                    )
                )
            except InternalServerError:
                return await context.respond(
                    embed=embeds.error(
                        'Ошибка Discord API',
                        description='Ошибка на стороне Discord, ничего поделать не можем.'
                    ),
                    components=View().add_item(Button(label='Страница статуса Discord',
                                                      url='https://discordstatus.com/'))
                )

        icon_of = client.config['icons']['type_of_user']

        embed: Embed = embeds.default(
            title=user.global_name if user.global_name else user.username,
            description=f'@{user.username}' if user.global_name else None,
            icon_url=icon_of['bot'] if user.is_bot else icon_of['user'],
            colour=user.accent_color
        )
        embed.set_thumbnail(user.display_avatar_url.url)
        embed.add_field(name='ID', value=str(user.id))
        embed.add_field(
            name='Создан',
            value=f"<t:{round(user.created_at.timestamp())}:R>\n"
                  f"(<t:{round(user.created_at.timestamp())}:D>)"
        )

        _embeds: [Embed] = [
            embed
        ]

        if user.banner_hash:
            embed.set_image(user.banner_url.url)
            view.add_item(Button(label='Ссылка на баннер', url=user.banner_url.url))

        if user.display_avatar_url:
            view.add_item(Button(label='Ссылка на аватарку', url=user.display_avatar_url.url))

        await context.respond(
            embeds=_embeds,
            components=view
        )
