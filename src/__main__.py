from asyncio.runners import Runner, run
from logging import getLogger, Logger
from sys import version_info

from crescent.client import Client
from hikari import GatewayBot, Intents, Status
from miru.bootstrap import install as miru_install
from uvloop import new_event_loop, install as uvloop_install

from __init__ import DISCORD_TOKEN
from bot import BotModel
from ext import ConfigurationFile

_log: Logger = getLogger(__name__)
config: dict = ConfigurationFile("data/config.yaml").get_config()

if __name__ == "__main__":

    async def main() -> None:
        base_bot: GatewayBot = GatewayBot(
            token=DISCORD_TOKEN,
            intents=Intents.GUILDS
                    | Intents.GUILD_EMOJIS
                    | Intents.GUILD_MESSAGES
                    | Intents.GUILD_VOICE_STATES,
            logs='DEBUG'
        )
        model: BotModel = BotModel(base_bot, config=config)
        client: Client = Client(base_bot, model)

        client.plugins.load_folder('extensions')
        miru_install(base_bot)

        await base_bot.start(status=Status.IDLE, check_for_updates=True)
        await base_bot.join()


    try:
        if version_info >= (3, 11):
            with Runner(loop_factory=new_event_loop) as runner:
                runner.run(main())
        else:
            uvloop_install()
            run(main())
    except KeyboardInterrupt:
        pass
