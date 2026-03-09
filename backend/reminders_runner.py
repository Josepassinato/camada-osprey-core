"""
Standalone runner for the Reminders Worker.
Connects to MongoDB independently and runs the reminder loop.
Designed to be launched as a separate PM2 process.
"""

import asyncio
import os
import sys

# Add parent to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from backend.reminders_worker import reminders_loop


async def main():
    mongo_url = os.environ.get("MONGODB_URI") or os.environ.get(
        "MONGO_URL", "mongodb://localhost:27017/"
    )
    db_name = os.environ.get("MONGODB_DB") or os.environ.get(
        "DB_NAME", "osprey_immigration_db"
    )

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # Verify connection
    await client.admin.command("ping")
    print(f"✅ Reminders Worker connected to MongoDB ({db_name})")

    try:
        await reminders_loop(db)
    except KeyboardInterrupt:
        print("Reminders Worker stopped")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
