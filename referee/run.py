"""
Module:
    ``run.py``

Purpose:
    Run the game asynchronously.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package. As expected, if the limit is exceeded, the agent will have
    lost the game.
"""

import asyncio
from time import time
from typing import AsyncGenerator

from .log import LogStream
from .game import Player, game, \
    GameUpdate, PlayerInitialising, GameBegin, TurnBegin, TurnEnd, \
    BoardUpdate, PlayerError, GameEnd, UnhandledError


async def run_game(players: list[Player],
                   event_handlers: list[AsyncGenerator | None]
                   ) -> Player | None:
    """
    Run a game, yielding event handler generators over the game updates.

    Args:
        players: the players list
        event_handlers: event handler to handle the event-driven game

    Returns:
        the winning player (interface) or 'None' if drawn.
    """

    async def _update_handlers(handlers: list[AsyncGenerator | None], updates: GameUpdate | None):
        """
        Helper function to handle the update.
        Args:
            handlers : the handlers
            updates  : specified update
        """
        for handler in handlers:
            try:
                if handler is not None:
                    await handler.asend(updates)
            except StopAsyncIteration:
                handlers.remove(handler)

    await _update_handlers(event_handlers, None)
    async for update in game(*players):
        await _update_handlers(event_handlers, update)
        match update:
            case GameEnd(winner, _):
                return winner


async def game_commentator(stream: LogStream) -> AsyncGenerator:
    """
    Intercepts game updates and provides some simple commentary.

    Args:
        stream: the log stream

    Returns:
        asynchronous interception
    """
    first_player_init = False
    while True:
        update: GameUpdate = yield
        match update:
            case PlayerInitialising(player):
                stream.info(f"Player {player} is initialising...")
                if first_player_init:
                    stream.info()
                first_player_init = True
            case GameBegin(_):
                stream.info()
                stream.info(f"Let the game begin!")
                stream.info()
            case TurnBegin(turn_id, player):
                stream.info(f"{player} to play (turn {turn_id}) ...")
                stream.info()
            case TurnEnd(_, player, action):
                stream.info()
                stream.info(f"{player} plays action {action}")
            case PlayerError(message):
                stream.error(f"player error: {message}")
            case GameEnd(None, _):
                stream.info(f"game ended in a draw")
            case GameEnd(winner, turn_id):
                stream.info(f"game over, winner is {winner}\nwin in {turn_id} turns")
            case UnhandledError(message):
                stream.error(f"fatal error: {message}")


async def game_event_logger(stream: LogStream) -> AsyncGenerator:
    """
    Intercepts all game events and logs them in a parseable format.
    Game events are logged as TSVs (tab-separated values), one per line, with
    the following format:

    .. math:: <time>\t<actor>\t<event>[\t<param_k>]*

    Where:
        - <time>     is the wall clock time since the game started (seconds).
        - <actor>    is either "referee" or the player colour.
        - <event>    is the event name.
        - <param_k>  k'th event argument (if applicable).

    Args:
        stream: log stream

    Returns:
        asynchronous interception
    """
    start_time = time()

    def _log(*params: str):
        update_time = time() - start_time
        stream.info(f"T{update_time:08.3f}\t" + "\t".join(params))

    def log_referee(*params: str):
        _log("referee", *params)

    def log_player(p: Player, *params: str):
        _log(str(p), *params)

    while True:
        update: GameUpdate = yield
        match update:
            case PlayerInitialising(player):
                log_player(player, "initialising")
            case GameBegin(_):
                log_referee("game_begin")
            case TurnBegin(turn_id, player):
                log_player(player, "turn_begin", f"{turn_id}")
            case TurnEnd(turn_id, player, action):
                log_player(player, "turn_end", f"{turn_id}", str(action))
            case BoardUpdate(_):
                log_referee("board_update")
            case GameEnd(win_player_id):
                log_referee("game_end", f"winner:{win_player_id}")
            case PlayerError(message):
                log_referee("player_error", message)
            case UnhandledError(message):
                log_referee("unhandled_error", message)
            case _:
                # Logger is expected to handle all game updates.
                raise NotImplementedError(f"unhandled game update: {update}")


async def game_delay(delay: float) -> AsyncGenerator:
    """
    Intercepts board updates and delays the game for a given amount of time.

    Args:
        delay: delay time
    Returns:
        asynchronous interception
    """
    while True:
        update: GameUpdate = yield
        match update:
            case BoardUpdate(_):
                await asyncio.sleep(delay)


async def game_user_wait(stream: LogStream) -> AsyncGenerator:
    """
    Intercepts board updates and waits for user input before continuing.

    Args:
        stream: log stream
    Returns:
        asynchronous interception
    """
    while True:
        update: GameUpdate = yield
        match update:
            case BoardUpdate(_):
                stream.info("press enter to continue ...")
                await asyncio.get_running_loop().run_in_executor(None, input)


async def output_board_updates(stream      : LogStream,
                               use_color   = False,
                               use_unicode = False,
                               width       : int = 66
                               ) -> AsyncGenerator:
    """
    Intercepts board updates and prints the new board state in the output stream.
    The board is formatted using the given options.

    Args:
        stream      : log stream
        use_color   : whether ansi color is applied
        use_unicode : whether unicode is used
        width       : the width of log printing

    Returns:
        asynchronous interception
    """
    while True:
        update: GameUpdate = yield
        match update:
            case BoardUpdate(board):
                stream.info(f"\n{' game board '.center(width, '=')}\n\n")
                stream.info(
                    '\n'.join([
                        f"{'':<7}{line}" for line in
                        board.render(
                            use_color=use_color,
                            use_unicode=use_unicode,
                        ).splitlines()
                    ])
                )
                stream.info(f"\n{''.center(width, '=')}\n\n")
