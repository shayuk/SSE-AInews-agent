from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio
import feedparser

app = FastAPI()

RSS_FEEDS = [
    "https://www.infoq.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://dev.to/feed/tag/ai",
    "https://towardsdatascience.com/tagged/ai/rss"
]

async def event_generator():
    while True:
        updates = []
        for url in RSS_FEEDS:
            feed = feedparser.parse(url)
            for entry in feed.entries[:1]:
                summary = entry.get("summary") or entry.get("description", "")
                updates.append(
                    f"🔹 {entry.title} — {entry.link}\n📝 Summary: {summary}"
                )

        yield {
            "event": "update",
            "data": "\n".join(updates)
        }
        await asyncio.sleep(3600)

@app.get("/sse")
async def sse_endpoint():
    return EventSourceResponse(event_generator())
    @app.get("/latest-news")
    async def latest_news():
        updates = []
        for url in RSS_FEEDS:
            feed = feedparser.parse(url)
            for entry in feed.entries[:1]:
                updates.append({
                    "title": entry.title,
                    "link": entry.link
                    "summary": entry.get("summary") or entry.get("description", "")  # אם יש, מציג. אם אין, מחזיר ריק
                })
        return {"news": updates}