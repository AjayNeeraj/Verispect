# calibrate.py — Run once to build real baselines for all probes
import asyncio
import httpx
import os
from dotenv import load_dotenv
from probes import PROBES
from database import init_db, save_baseline, get_baseline

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

async def calibrate():
    await init_db()
    print(f"Starting calibration — {len(PROBES)} probes to process...\n")

    calibrated = 0
    skipped = 0

    async with httpx.AsyncClient(timeout=60.0) as client:
        for probe in PROBES:
            existing = await get_baseline(probe["id"])
            if existing:
                print(f"  SKIP  {probe['id']} — baseline already exists")
                skipped += 1
                continue

            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json={"model": "gpt-4o-mini", "messages": probe["messages"]},
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            )
            data = response.json()

            if "error" in data:
                print(f"  ERROR {probe['id']} — {data['error'].get('message', 'Unknown error')}")
                continue

            text = data["choices"][0]["message"]["content"]

            await save_baseline(probe["id"], "gpt-4o-mini", text)
            calibrated += 1
            category = probe.get("category", "unknown")
            print(f"  DONE  {probe['id']} [{category}]")
            print(f"        {text[:120]}...")
            print()

    print(f"\nCalibration complete. {calibrated} new baselines stored, {skipped} skipped.")

asyncio.run(calibrate())