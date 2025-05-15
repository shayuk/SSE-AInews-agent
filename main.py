from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio
import feedparser

app = FastAPI()

# רשימת מקורות חדשות מעולמות ה-AI והפיתוח
RSS_FEEDS = [
    "https://www.infoq.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://dev.to/feed/tag/ai",
    "https://towardsdatascience.com/tagged/ai/rss"
]

# ✅ נקודת גישה רגילה שמחזירה JSON של כתבות לפי מילה
@app.get("/ai-news")
async def ai_news(keyword: str = "cursor"):
    updates = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                content = (entry.title + " " + entry.get("summary", "")).lower()
                if keyword.lower() in content:
                    updates.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.get("summary") or entry.get("description", ""),
                        "published": entry.get("published", ""),
                        "source": feed.feed.title
                    })
        except Exception:
            continue

    updates.sort(key=lambda x: x["published"] if x["published"] else "", reverse=True)

    return {
        "status": "success",
        "keyword": keyword,
        "count": len(updates),
        "news": updates
    }

# 📡 נקודת גישה בשידור חי שמתאימה ל-MCP / Cursor
@app.get("/sse")
async def sse_endpoint():
    async def event_generator():
        while True:
            updates = []
            keyword = "cursor"  # אפשר לשנות ל־GPT או AI

            for url in RSS_FEEDS:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:5]:
                        content = (entry.title + " " + entry.get("summary", "")).lower()
                        if keyword in content:
                            summary = entry.get("summary") or entry.get("description", "")
                            source = feed.feed.get("title", "")
                            updates.append(f"🔹 {entry.title} ({source}) — {entry.link}\n📝 {summary}")
                except Exception:
                    continue

            yield {
                "event": "update",
                "data": "\n\n".join(updates) if updates else "No new relevant updates at this time."
            }
            await asyncio.sleep(3600)  # עדכון פעם בשעה

    return EventSourceResponse(event_generator())
