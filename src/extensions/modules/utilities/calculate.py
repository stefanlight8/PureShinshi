from datetime import timedelta

from crescent.commands import command, option, hook
from crescent.context import Context
from crescent.ext.cooldowns import cooldown

from bot import BotModel, Plugin
from ext import embeds

plugin = Plugin()


@plugin.include
@hook(cooldown(3, timedelta(seconds=15)))
@command(name='calculate', description='Нужно посчитать что-нибудь?')
class Command:
    expression = option(str, description='Ваш пример, который нужно решить', max_length=200)

    async def callback(self, context: Context) -> None:
        client: BotModel = context.client.model
        result: str = "Решения нет"

        try:
            async with client.session.request(
                    'POST',
                    url='https://api.mathjs.org/v4/',
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={"expr": str(self.expression)}
            ) as response:
                response = await response.json()
        except (Exception,):
            return await context.respond(
                embed=embeds.error(
                    title="Ошибка калькулятора",
                    description="По всей видимости API не ответило"
                )
            )

        if not response['error']:
            if isinstance(response['result'], str):
                result = response['result'].replace("`", "\u200b`\u200b")[:500]
            elif isinstance(response['result'], list):
                result = '\n'.join(response['result']).replace("`", "\u200b`\u200b")[:500]

            if any(bad_response in response['result'] for bad_response in ('NaN', 'Error')):
                return await context.respond(
                    embed=embeds.error(
                        title="Ошибка калькулятора",
                        description="API не смогло вывести нормальное число.\n"
                                    "Попробуйте изменить пример или его порядок.",
                        icon_url=client.config['icons']['errors']['calculate']
                    )
                )

        return await context.respond(
            embed=(
                embeds.default(
                    title='Калькулятор',
                    icon_url=client.config['icons']['calculate']
                )
                .set_footer(text='Powered by api.mathjs.org.')
                .add_field(name='Пример', value=self.expression)
                .add_field(
                    name='Результат',
                    value=result
                )
            )
        )
