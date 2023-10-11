from crescent import Context, command, option, hook
from hikari import User, Permissions, InteractionMember, GatewayBot, ForbiddenError, NotFoundError

from bot import Plugin, BotModel
from ext import embeds
from ext.checks import has_permissions

plugin = Plugin()


@plugin.include
@hook(has_permissions(Permissions.KICK_MEMBERS))
@command(name='kick', description='Выгнать пользователя с сервера')
class Command:
    user = option(User, description='Выберете или найдите пользователя из списка')
    reason = option(str, description='Укажите причину', max_length=200, default=None)

    async def callback(self, context: Context) -> None:
        assert isinstance(context.app, GatewayBot)

        client: BotModel = context.client.model
        bot_member = context.guild.get_member(context.app.get_me())

        assert isinstance(self.user, InteractionMember)
        assert isinstance(context.member, InteractionMember)
        assert isinstance(bot_member, InteractionMember)

        if not self.user.guild_id:
            return await context.respond(
                embed=embeds.error(
                    'Вы не можете выгнать пользователя',
                    'Поскольку он не находится на сервере',
                    icon_url=client.config['icons']['errors']['moderate']
                ),
                ephemeral=True
            )
        elif self.user.id == context.member.id:
            return await context.respond(
                embed=embeds.error(
                    'Вы не можете выгнать самого себя',
                    'Хотя в принципе можете - есть прекрасная кнопка "Выйти с сервера"',
                    icon_url=client.config['icons']['errors']['moderate']
                ),
                ephemeral=True
            )
        elif self.user.is_bot:
            return await context.respond(
                embed=embeds.error(
                    'Вы не можете выгнать пользователя',
                    'Поскольку он является ботом',
                    icon_url=client.config['icons']['errors']['moderate']
                ),
                ephemeral=True
            )
        elif context.member.get_top_role().position <= self.user.get_top_role().position:
            return await context.respond(
                embed=embeds.error(
                    'Вы не можете выгнать пользователя',
                    'Который находится выше вас по роли',
                    icon_url=client.config['icons']['errors']['moderate']
                ),
                ephemeral=True
            )
        elif bot_member.get_top_role().position <= self.user.get_top_role().position:
            return await context.respond(
                embed=embeds.error(
                    'Вы не можете выгнать пользователя',
                    'Который находится выше бота по роли',
                    icon_url=client.config['icons']['errors']['moderate']
                ),
                ephemeral=True
            )

        try:
            await context.guild.kick(
                self.user,
                reason=f"[{context.member} ({context.member.id})] {self.reason or 'Причина отсутствует'}"
            )

            try:
                await self.user.send(
                    embed=(
                        embeds.default(
                            f'Вас выгнали с {context.guild.name}'
                        )
                        .set_thumbnail(context.guild.icon_url.url)
                        .add_field(
                            name='Модератор',
                            value=f'@{context.member.username} (ID: {context.member.id})'
                        )
                        .add_field(name='Причина', value=self.reason or 'Отсутствует')
                    )
                )
            except (Exception,):
                pass
        except NotFoundError:
            return await context.respond(
                embed=embeds.error(
                    title='Участник не был найден',
                    icon_url=client.config['icons']['errors']['moderate']
                )
            )
        except ForbiddenError:
            return await context.respond(
                embed=embeds.error(
                    title='У бота недостаточно прав для выполнения данной команды',
                    icon_url=client.config['icons']['errors']['moderate']
                )
            )
        except (Exception,):
            return await context.respond(
                embed=embeds.error(
                    'Что-то пошло не так',
                    f"Обратитесь в нашу [поддержку]({client.config['bot']['links'][0]['url']})",
                    client.config['icons']['errors']['moderate']
                )
            )
        else:
            return await context.respond(
                embed=(
                    embeds.default(
                        f'Пользователь @{self.user.username} был выгнан с сервера',
                        icon_url=client.config['icons']['moderate']
                    )
                    .set_thumbnail(self.user.display_avatar_url.url)
                    .add_field(name='ID нарушителя', value=str(self.user.id))
                    .add_field(name='Причина', value=self.reason or 'Отсутствует')
                    .set_footer(
                        text=f'Модератор: @{context.member.username} (ID: {context.member.id})',
                        icon=context.member.display_avatar_url.url
                    )
                )
            )
