# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2015-2016 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
from collections import namedtuple

from . import utils
from .mixins import Hashable

PartialEmoji = namedtuple('PartialEmoji', 'id name')

class Emoji(Hashable):
    """Represents a custom emoji.

    Depending on the way this object was created, some of the attributes can
    have a value of ``None``.

    Supported Operations:

    +-----------+-----------------------------------------+
    | Operation |               Description               |
    +===========+=========================================+
    | x == y    | Checks if two emoji are the same.       |
    +-----------+-----------------------------------------+
    | x != y    | Checks if two emoji are not the same.   |
    +-----------+-----------------------------------------+
    | hash(x)   | Return the emoji's hash.                |
    +-----------+-----------------------------------------+
    | iter(x)   | Returns an iterator of (field, value)   |
    |           | pairs. This allows this class to be     |
    |           | used as an iterable in list/dict/etc.   |
    |           | constructions.                          |
    +-----------+-----------------------------------------+
    | str(x)    | Returns the emoji rendered for discord. |
    +-----------+-----------------------------------------+

    Attributes
    -----------
    name: str
        The name of the emoji.
    id: int
        The emoji's ID.
    require_colons: bool
        If colons are required to use this emoji in the client (:PJSalt: vs PJSalt).
    managed: bool
        If this emoji is managed by a Twitch integration.
    guild: :class:`Guild`
        The guild the emoji belongs to.
    roles: List[:class:`Role`]
        A list of :class:`Role` that is allowed to use this emoji. If roles is empty,
        the emoji is unrestricted.
    """
    __slots__ = ('require_colons', 'managed', 'id', 'name', 'roles', 'guild', '_state')

    def __init__(self, *, guild, state, data):
        self.guild = guild
        self._state = state
        self._from_data(data)

    def _from_data(self, emoji):
        self.require_colons = emoji['require_colons']
        self.managed = emoji['managed']
        self.id = int(emoji['id'])
        self.name = emoji['name']
        self.roles = emoji.get('roles', [])
        if self.roles:
            roles = set(self.roles)
            self.roles = [role for role in self.guild.roles if role.id in roles]

    def _iterator(self):
        for attr in self.__slots__:
            if attr[0] != '_':
                value = getattr(self, attr, None)
                if value is not None:
                    yield (attr, value)

    def __iter__(self):
        return self._iterator()

    def __str__(self):
        return "<:{0.name}:{0.id}>".format(self)

    def __repr__(self):
        return '<Emoji id={0.id} name={0.name!r}>'.format(self)

    @property
    def created_at(self):
        """Returns the emoji's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def url(self):
        """Returns a URL version of the emoji."""
        return "https://discordapp.com/api/emojis/{0.id}.png".format(self)


    @asyncio.coroutine
    def delete(self):
        """|coro|

        Deletes the custom emoji.

        You must have :attr:`Permissions.manage_emojis` permission to
        do this.

        Guild local emotes can only be deleted by user bots.

        Raises
        -------
        Forbidden
            You are not allowed to delete emojis.
        HTTPException
            An error occurred deleting the emoji.
        """

        yield from self._state.http.delete_custom_emoji(self.guild.id, self.id)

    @asyncio.coroutine
    def edit(self, *, name):
        """|coro|

        Edits the custom emoji.

        You must have :attr:`Permissions.manage_emojis` permission to
        do this.

        Guild local emotes can only be edited by user bots.

        Parameters
        -----------
        name: str
            The new emoji name.

        Raises
        -------
        Forbidden
            You are not allowed to edit emojis.
        HTTPException
            An error occurred editing the emoji.
        """

        yield from self._state.http.edit_custom_emoji(self.guild.id, self.id, name=name)