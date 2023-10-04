from datetime import timedelta

from crescent.commands import command, option, hook
from crescent.context import Context
from crescent.ext.cooldowns import cooldown

from bot import Plugin
from ext import embeds
from ext.api import Request

plugin = Plugin()


@plugin.include
@hook(cooldown(1, timedelta(seconds=10)))
@command(name='calculate', description='Нужно посчитать что-нибудь?')
class Command:
    expression = option(str, description='Ваш пример, который нужно решить', max_length=200)

    async def callback(self, context: Context) -> None:
        try:
            response = await Request.json(
                method='POST',
                url='https://api.mathjs.org/v4/',
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) "
                                  "Gecko/20100101 Firefox/118.0",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache"
                },
                json={"expr": str(self.expression)}
            )
        except Exception as exception:
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
