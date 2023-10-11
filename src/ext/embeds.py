from hikari import Embed

from __main__ import config

__all__ = ['default', 'error']


def default(
        title: str = None,
        description: str = None,
        icon_url: str = None,
        colour: hex = 0xFFCE4F,
        **kwargs
) -> Embed:
    embed = Embed(colour=colour, description=description, **kwargs)

    if title or title and icon_url:
        embed.set_author(name=title, icon=icon_url)

    return embed


def error(
        title: str = None,
        description: str = None,
        icon_url: str = config["icons"]["errors"]["default"],
        colour: hex = 0xED4245,
        **kwargs
) -> Embed:
    embed = default(
        title=title, icon_url=icon_url, description=description, colour=colour, **kwargs
    )
    return embed
