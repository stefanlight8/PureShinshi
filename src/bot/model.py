from asyncio import get_running_loop
from logging import getLogger, Logger

from aiohttp import ClientSession
from crescent.plugin import Plugin as BasePlugin
from hikari.events import (
    StartingEvent,
    StartedEvent,
    ShardConnectedEvent,
    ShardReadyEvent,
    StoppingEvent,
    StoppedEvent
)
from hikari.impl import GatewayBot
from hikari.presences import Status, Activity, ActivityType

__all__ = ['BotModel', 'Plugin']
_log: Logger = getLogger(__name__)


class BotModel:
    """
    Base model of a bot.
    """
    __slots__ = ['_bot', 'session', 'database', 'node_pool', 'config']

    def __init__(self, bot: GatewayBot, **kwargs) -> None:
        self._bot: GatewayBot = bot

        self.session: ClientSession | None = None
        self.database: None = kwargs.get('database')
        self.node_pool: None = kwargs.get('node_pool')
        self.config: dict = kwargs.get('config')

        events = {
            StartingEvent: self.on_starting,
            StartedEvent: self.on_start,
            ShardConnectedEvent: self.on_shard_connect,
            ShardReadyEvent: self.on_shard_ready,
            StoppingEvent: self.on_stopping,
            StoppedEvent: self.on_stop
        }

        for event, callback in events.items():
            bot.subscribe(event, callback)

    def init_music_nodes(self, user_id) -> None:
        if self.node_pool:
            _log.debug('Initializing music nodes...')
            for node_data in self.config['nodes']:
                node = self.node_pool.create_node(
                    host=node_data['host'],
                    port=node_data['port'],
                    password=node_data['password'],
                    user_id=user_id,
                    name=node_data['name']
                )
                node.connect()

            _log.info('Initialized music nodes!')
        else:
            _log.warning("Node pool is none")

    @staticmethod
    async def on_starting(_: StartingEvent) -> None:
        _log.info("Bot is starting...")

    async def on_start(self, _: StartedEvent) -> None:
        self.session = ClientSession(loop=get_running_loop())
        _log.info("Bot is started successfully")

    @staticmethod
    async def on_shard_connect(event: ShardConnectedEvent) -> None:
        _log.info(f"Shard is connected successfully (SHARD_ID {event.shard.id})")

    async def on_shard_ready(self, event: ShardReadyEvent) -> None:
        await event.shard.update_presence(
            status=Status.ONLINE,
            activity=Activity(
                name=f"Кластер #{event.shard.id}", type=ActivityType.WATCHING
            ),
        )
        _log.info(f"Shard is ready (ID {event.shard.id})")

        self.init_music_nodes(event.my_user.id)

        if self.database:
            self.database.connect()
        else:
            _log.warning("Database is none")

    async def on_stopping(self, _: StoppingEvent) -> None:
        _log.info("Bot is stopping...")

        if self.database:
            await self.database.disconnect()

        if self.node_pool:
            for node in self.node_pool.nodes:
                await node.close()

    @staticmethod
    async def on_stop(_: StoppedEvent) -> None:
        _log.info("Bot is stopped successfully, bye-bye!")
        exit(0)


Plugin = BasePlugin[GatewayBot, BotModel]
