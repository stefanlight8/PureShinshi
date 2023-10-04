from crescent.commands import command, option
from crescent.commands.groups import Group
from crescent.context import Context
from hikari import User
from miru.button import Button
from miru.view import View

from bot import Plugin
from ext import embeds

plugin = Plugin()
group = Group('member', dm_enabled=False)


async def unknown_error_response(context: Context) -> None:
    return await context.respond(
        embed=embeds.error(
            "Произошла неизвестная ошибка",
            description="По всей видимости у данного пользователя нет аватарки",
        )
    )


@plugin.include
@group.child
@command(name="avatar", description="Получить свой аватар или пользователя")
class Command:
    user: User = option(User, description="Кого аватарку вы хотите получить", default=None)

    async def callback(self, context: Context) -> None:
        view: View = View()

        if not self.user:
            user = context.member
        else:
            user = self.user

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
