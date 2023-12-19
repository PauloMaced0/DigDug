"""Example client."""
import asyncio
import getpass
import json
import os
from collections import deque

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame
import websockets

from tree_search import SearchProblem, SearchTree
from moveDigDug import DigDug 

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                path = ()

                if 'map' in state:
                    key = ""
                    digdug_dir = 0
                    game_map = state['map']

                if (key == 'w'): 
                    digdug_dir = 0
                elif(key == 'd'): 
                    digdug_dir = 1
                elif(key == 's'): 
                    digdug_dir = 2
                elif(key == 'a'): 
                    digdug_dir = 3

                if 'enemies' in state and state['enemies']:
                    #print(state)
                    my_x, my_y = state['digdug']
                    game_map[my_x][my_y] = 0
                    state['map'] = game_map
                    state['digdug_dir'] = digdug_dir
                    p = SearchProblem(DigDug(state), state, 0)
                    t = SearchTree(p)
                    path = t.search()

                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = path if path else ""

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
            except websockets.exceptions.ConnectionClosedOK:
                print(state['score'])
                #print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))

