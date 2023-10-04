from re import compile
from typing import cast

from crescent.commands import command, option, hook
from crescent.context import Context
from hikari import GatewayBot
from lavaplay import Node, Track, PlayList
from lavaplay.player import Player
from miru import View, Button, SelectOption, TextSelect, ViewContext
from music.hooks import check_connection_hook
from music.join_function import join

from bot import Plugin
from ext import embeds

plugin = Plugin()
URL_REGEX = compile(r'https?://(?:www\.)?.+')


class SelectTrack(TextSelect):
    def __init__(self, player: Player, tracks: list[Track]):
        self.tracks = tracks
        self.player: Player = player

        tracks_options = []

        for track in tracks[:10]:
            if track.title not in [available_track.label for available_track in tracks_options]:
                tracks_options.append(
                    SelectOption(label=track.title, description=track.author, value=str(track))
                )

        super().__init__(
            options=tracks_options
        )

    async def callback(self, context: ViewContext) -> None:
        track: Track = [
            track for track in self.tracks if str(track) == context.interaction.values[0]
        ][0]
        await self.player.play(track, requester=context.member.id)
        await context.respond(
            f"В очередь была добавлена композиция [{track.author} - {track.title}]({track.uri})",
            components=View().add_item(Button(label="Ссылка", url=track.uri)),
        )


@plugin.include
@hook(check_connection_hook)
@command(name='play', description='Послушать музыку? Без проблем - one momento!')
class Command:
    query: str = option(
        str, description='Что будем играть? (Запрос / Ссылка Spotify, Яндекс Музыка, SoundCloud)', max_length=200
    )

    async def callback(self, context: Context) -> None:
        bot: GatewayBot = cast(GatewayBot, context.app)
        node: Node = context.client.model.node_pool.default_node

        if not node:
            return await context.respond(
                embed=embeds.default(
                    title='Извиняемся за неудобства',
                    description='На данный момент музыкальные сервера отсутствуют, так что мы не можем проиграть песню'
                )
            )

        if not bot.cache.get_voice_state(context.guild, bot.get_me()):
            await join(context)

        player: Player = node.get_player(context.guild_id)

        if URL_REGEX.match(self.query):
            tracks = await node.get_tracks(self.query)

            if not tracks:
                return await context.respond(
                    embed=embeds.error(
                        'Трек/плейлист не был найден',
                        description='Попробуйте изменить URL'
                    )
                )
            else:
                if isinstance(tracks, PlayList):
                    _tracks = tracks.tracks[:20]
                    player.add_to_queue(_tracks, requester=context.member.id)
                    await context.respond(
                        f'В очередь было добавлено **{len(_tracks)} позиций** из плейлиста **{tracks.name}**'
                    )
                else:
                    track: Track = tracks[0]
                    await player.play(track, requester=context.member.id)
                    await context.respond(
                        f'В очередь была добавлена композиция [{track.author} - {track.title}]({track.uri})',
                        components=View().add_item(Button(label='Ссылка', url=track.uri))
                    )
        else:
            tracks = await node.get_tracks(f'{self.query}')

            if not tracks:
                return await context.respond(
                    embed=embeds.error(
                        "Трек/плейлист не был найден", description="Попробуйте использовать URL"
                    )
                )
            elif len(tracks) == 1:
                await player.play(tracks[0], requester=context.member.id)
            else:
                await context.respond(components=View().add_item(SelectTrack(player, tracks)))
