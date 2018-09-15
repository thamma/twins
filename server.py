#!/usr/bin/env python

import asyncio
import websockets
import json
import enum

from stategraph import Graph
Graph.gamestate.save()


class Notify(enum.Enum):
    GOGO = '{"type": "gogo"}'
    WAIT = '{"type": "wait"}'
    NOPE = '{"type": "nope"}'


class Client:
    clients = set()

    def __init__(self, socket):
        if len(self.clients) >= 2:
            raise ValueError("game full")

        self.socket = socket
        self.id = 0
        if len(self.clients) > 0 and list(self.clients)[0].id == 0:
            self.id = 1
        self.clients.add(self)

    @classmethod
    async def notify_all(cls, msg: Notify):
        if cls.clients:
            await asyncio.wait([c.socket.send(msg.value) for c in cls.clients])

    @classmethod
    async def update_all(cls):
        if cls.clients:
            await asyncio.wait([c.update() for c in cls.clients])

    async def handler(self):
        if len(self.clients) == 2:
            await self.update_all()
            await self.notify_all(Notify.GOGO)
        async for message in self.socket:
            Graph.step(self.id, message)
            await self.update_all()

    async def update(self):
        transitions = Graph.get_transitions(self.id)
        await self.socket.send(json.dumps({"type": "state", "state": transitions}))

    async def close(self):
        self.clients.remove(self)
        await self.notify_all(Notify.WAIT)


async def client_handler(websocket, path: str):
    (remote_host, remote_port) = websocket.remote_address
    remote = f"{remote_host:>15}:{remote_port:<5}"

    print(f"{'Connect':<10} {remote} {path}")

    try:
        msg = await websocket.recv()
    except websockets.exceptions.ConnectionClosed:
        print(f"{'Lost':<10} {remote}")
        return

    print(f"{'Handshake':<10} {remote}")

    if msg == "really_makes_you_admin":
        print(f"{'Admin':<10} {remote}")
        try:
            await admin_handler(websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            print(f"{'Admin exit':<10} {remote}")
            return
    try:
        client = Client(websocket)
    except ValueError:
        print(f"{'Reject':<10} {remote}")
        await websocket.send(Notify.NOPE.value)
        return

    print(f"{'Join':<10} {remote} client {client.id}")

    try:
        await client.handler()
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await client.close()
        print(f"{'Disconnect':<10} {remote}")


async def admin_handler(websocket):

    with open("res/b.png", "rb") as f:
        import base64
        s = base64.b64encode(f.read())

    await websocket.send(json.dumps({
        "type": "state",
        "state": {
            "text": "You are an admin :D",
            "image": "data:image;base64," + s.decode(),
            "transitions": {
                "reset": "Reset",
                "env": "Print env",
                "vegan0": "Make player 0 vegan",
                "vegan1": "Make player 1 vegan",
                "tetra": "Test tetra",
                "ktane": "Test ktane"
            }
        }
    }))
    await websocket.send(Notify.GOGO.value)
    async for msg in websocket:
        print(f"{'Admin Cmd':<10} {msg}")
        if msg == "reset":
            Graph.gamestate.reset()
        elif msg == "env":
            print("===== Env =====")
            for k in Graph.gamestate.env:
                print(k, Graph.gamestate.env[k])
            print("===============")
            continue
        elif msg == "tetra":
            Graph.gamestate.pos[0] = "maze_0_1"
            Graph.gamestate.pos[1] = "maze_10_0"
            await Client.update_all()
        elif msg == "ktane":
            Graph.gamestate.pos[0] = "ktane_spawn_A"
            Graph.gamestate.pos[1] = "ktane_spawn_B"
        elif msg == "vegan0":
            Graph.gamestate.env["vegan"] = 0
        elif msg == "vegan1":
            Graph.gamestate.env["vegan"] = 1
        await Client.update_all()

start_server = websockets.serve(client_handler, '0.0.0.0', 51862)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
