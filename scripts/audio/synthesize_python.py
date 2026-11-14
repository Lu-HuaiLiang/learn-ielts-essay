import asyncio
import sys

import edge_tts


async def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: synthesize_python.py <text> <output>')
    await edge_tts.Communicate(sys.argv[1], 'en-US-AriaNeural').save(sys.argv[2])


asyncio.run(main())
