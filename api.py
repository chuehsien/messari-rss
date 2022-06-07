from RSSArticle import RSSArticle
from RSSFeed import RSSFeed
from fastapi import FastAPI
from pydantic import BaseModel
import db
from typing import Union
from utils import makeFeedId

app = FastAPI()

class FeedObject(BaseModel):
    url: Union[str, None] = None
    pattern: Union[str, None] = None


@app.get("/")
async def root():
    return {"message": "Hello to messari RSS api"}


@app.get("/feed",response_model=list[RSSFeed])
async def get_feeds():
    return db.get_feeds()

@app.get("/articles",response_model=list[RSSArticle])
async def get_articles():
    return db.get_articles()



@app.post("/feed")
async def add_feed(feed: FeedObject):
    if (feed.url is None):
        return {"message": "URL required"}
    rss_feed = RSSFeed(url=feed.url,pattern=feed.pattern)
    if (not db.feed_exists(rss_feed.id)):
        db.create_feed(rss_feed, rss_feed.id)
        return {"message": f"Feed {rss_feed.id} created"}
    else:
        return {"message": f"Feed {rss_feed.id} already exists"}



@app.post("/feed/{feed_id}")    
async def edit_feed(feed_id: str, edits: FeedObject):
    rss_feed = db.get_feed(feed_id)
    if (rss_feed is None):
        return {"message": "Don't exist"}
    idChanged = False
    if (rss_feed is not None):
        if (edits.url is not None):
            rss_feed["url"] = edits.url
        
        if (edits.pattern is not None):
            rss_feed["pattern"] = edits.pattern

        if (edits.url is not None or edits.pattern is not None):
            rss_feed["id"] = makeFeedId(edits.url if edits.url is not None else rss_feed["url"], 
                edits.pattern if edits.pattern is not None else rss_feed["pattern"])

            idChanged = True

        # these shouldn't be edited
        # if (edits.lastBuildTimestamp is not None):
        #     rss_feed.lastBuildTimestamp = edits.lastBuildTimestamp
        # if (edits.lastQueriedTimestamp is not None):
        #     rss_feed.lastQueriedTimestamp = edits.lastQueriedTimestamp
        # if (edits.lastResult is not None):
        #     rss_feed.lastResult = edits.lastResult


        if (idChanged):
            rss_feed["forceRefresh"] = True
            db.delete_feed(feed_id)
            db.create_feed(rss_feed, rss_feed['id'])
            return {"message": f"Feed {feed_id} deleted, {rss_feed['id']} created"}
        else:
            r = db.update_feed(feed_id, rss_feed)
            return {"message": f"Feed {feed_id} modified: {r}"}


@app.delete("/feed/{feed_id}")    
async def delete_feed(feed_id):
    if (db.feed_exists(feed_id)):
        r = db.delete_feed(feed_id)
        return {"message": f"Removed {feed_id}: {r}"}
    else:
        return {"message": f"Feed {feed_id} does not exist"}

# for processor to use

@app.get("/processor/exists/{article_id}")
async def article_exists(article_id):
    return db.article_exists(article_id)

@app.post("/processor/add_article")
async def add_article(article: RSSArticle):
    if not db.article_exists(article.id):
        db.create_article(article)
        return {"message": f"Created article {article.id}"}
    else:
        return {"message": f"Article {article.id} exists"}

@app.post("/processor/update_feed_stats")
async def update_feed_stats(feed: RSSFeed):
    if db.feed_exists(feed.id):
        db.update_feed(feed.id, feed)
        return {"message": f"Updated feed {feed.id}"}
    else:
        return {"message": f"Feed {feed.id} does not exist"}


@app.delete("/processor/delete_articles")
async def delete_articles():
    db.drop_articles()