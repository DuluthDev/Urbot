import json
import dumper
import urlock
import asyncio

from botConfig import *
from nio import AsyncClient, MatrixRoom, RoomMessageText


async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    print(
        f"Message received in room {room.display_name}\n"
        f"{room.user_name(event.sender)} | {event.body}"
    )


async def urbitMessageHandling() -> None:
    zod = urlock.Urlock(shipUrl, shipCode)
    zod.connect()
    zod.subscribe("zod", "chat-view", "/primary")

    pipe = zod.sse_pipe()

    for m in pipe.events():
        zod.ack(int(m.id))
        parsedMessage = m.data.split("'")
        dumper.dump(parsedMessage)

async def matrixMessageHandling() -> None:
    client = AsyncClient(matrixHomeServer, matrixBotUser)
    client.add_event_callback(message_callback, RoomMessageText)

    print(await client.login(matrixBotPass))
    # "Logged in as @alice:example.org device id: RANDOMDID"

    # If you made a new room and haven't joined as that user, you can use
    await client.join(matrixRoom)

    await client.room_send(
        # Watch out! If you join an old room you'll see lots of old messages
        room_id=matrixRoom,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": "Hello world!"
        }
    )

    await client.sync_forever(timeout=30000)  # milliseconds


async def main() -> None:
    await asyncio.gather(
        matrixMessageHandling(),
        urbitMessageHandling()
    )

asyncio.get_event_loop().run_until_complete(main())
