from __future__ import annotations
from .test_info import test_info
from sideral import entity
from sideral import id
from sideral import column
from sideral import join
from sideral import counter_join
from sideral import join_table
from sideral import many_to_many
from sideral import load


@entity
class Account:

    __test_schema__ = ['id', 'username']

    __test_columns__ = [
        test_info(attribute_name = 'id', strategy = load.EAGER, column = 'id'),
        test_info(attribute_name = 'username', strategy = load.EAGER, column = 'username'),
    ]

    __test_relationships__ = [
        test_info(
            attribute_name = 'followers',
            strategy = load.LAZY,
            mapping = 'following',
            column = 'id_account',
            second_column = 'id_follower',
            second_table = 'Follow',
            type = 'ToMany',
            reference = 'Account'
        ),
        test_info(
            attribute_name = 'following',
            strategy = load.LAZY,
            mapping = 'followers',
            column = 'id_follower',
            second_column = 'id_account',
            second_table = 'Follow',
            type = 'ToMany',
            reference = 'Account'
        )
    ]
    
    def __init__(self, id: int = ..., username: str = ..., followers: list[Account] = ..., following: list[Account] = ...) -> None:
        self._id = id
        self._username = username
        self._followers = [] if followers is ... else followers
        self._following = [] if followers is ... else following
    
    @id
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, id: int) -> None:
        self._id = id
    
    @column
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @counter_join(column_name = 'id_follower')
    @join(column_name = 'id_account')
    @join_table(name = 'Follow')    
    @many_to_many(mapping = 'following', master = True)
    def followers(self) -> list[Account]:
        return self._followers
    
    @followers.setter
    def followers(self, followers: list[Account]) -> None:
        self._followers = followers
    
    @many_to_many(mapping = 'followers')
    def following(self) -> list[Account]:
        return self._following
    
    @following.setter
    def following(self, following: list[Account]) -> None:
        self._following = following