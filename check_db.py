import aiosqlite
import asyncio

async def check():
    async with aiosqlite.connect("verispect.db") as db:
        async with db.execute("SELECT * FROM logs") as cursor:
            rows = await cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No rows yet")

asyncio.run(check())

