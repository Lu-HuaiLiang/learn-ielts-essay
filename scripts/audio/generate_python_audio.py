import asyncio
import json
import os
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "public" / "audio" / "essays"
VOICE = "en-US-AriaNeural"
CONCURRENCY = int(os.environ.get("AUDIO_CONCURRENCY", "8"))


async def synthesize(item, semaphore):
    output = ROOT / "site" / "public" / item["path"]
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_file() and output.stat().st_size >= 128:
        return False
    temporary = output.with_suffix(output.suffix + f".tmp-{os.getpid()}")
    async with semaphore:
        for attempt in range(3):
            try:
                await edge_tts.Communicate(item["text"], VOICE).save(str(temporary))
                temporary.replace(output)
                return True
            except Exception:
                temporary.unlink(missing_ok=True)
                if attempt == 2:
                    raise
                await asyncio.sleep(attempt + 1)


async def main():
    essays = json.loads((ROOT / "data" / "essays.json").read_text())
    items = []
    for essay in essays:
        for index, paragraph in enumerate(essay["paragraphs"]):
            items.append({
                "essayId": essay["id"],
                "text": paragraph.replace("**", "").strip(),
                "path": f"audio/essays/{essay['id']}/p{index + 1:02d}.mp3",
            })
    semaphore = asyncio.Semaphore(CONCURRENCY)
    completed = 0
    for start in range(0, len(items), CONCURRENCY):
        batch = items[start:start + CONCURRENCY]
        results = await asyncio.gather(*(synthesize(item, semaphore) for item in batch))
        completed += sum(results)
        print(f"Generated {min(start + CONCURRENCY, len(items))}/{len(items)} ({completed} new)", flush=True)


asyncio.run(main())
