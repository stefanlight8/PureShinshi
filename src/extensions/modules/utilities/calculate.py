from datetime import timedelta

from crescent.commands import command, option, hook
from crescent.context import Context
from crescent.ext.cooldowns import cooldown

from bot import Plugin
from ext import embeds

plugin = Plugin()


@plugin.include
@hook(cooldown(1, timedelta(seconds=10)))
@command(name='calculate', description='Нужно посчитать что-нибудь?')
class Command:
    expression = option(str, description='Ваш пример, который нужно решить', max_length=200)

    async def callback(self, context: Context) -> None:
        try:
            async with context.client.model.session.request(
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
            result: str

            if isinstance(response['result'], str):
                result = response['result'].replace("`", "\u200b`\u200b")[:500]
            elif isinstance(response['result'], list):
                result = '\n'.join(response['result']).replace("`", "\u200b`\u200b")[:500]
            else:
                result = 'Решения нет'
        else:
            if "Error" in response['error']:
                return await context.respond(
                    embed=embeds.error(
                        title="Ошибка калькулятора",
                        description="API не смог понять пример.\n"
                                    "Попробуйте изменить пример или его порядок.",
                    )
                )

            if "NaN" in response['error']:
                return await context.respond(
                    embed=embeds.error(
                        title="Ошибка калькулятора",
                        description="API не смогло вывести нормальное число.\n"
                                    "Попробуйте изменить пример или его порядок.",
                    )
                )

        return await context.respond(
            embed=(
                embeds.default(
                    title='Калькулятор',
                    description='Powered by [api.mathjs.org](https://api.mathjs.org/)'
                )
                .add_field(name='Пример', value=self.expression)
                .add_field(
                    name='Результат',
                    value=result
                )
            )
        )
