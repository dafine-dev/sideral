from __future__ import annotations
from sideral import entity, id, column, join_table, join, counter_join, many_to_many


@entity
class Account:
    
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