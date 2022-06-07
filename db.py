from RSSArticle import RSSArticle
from RSSFeed import RSSFeed
from tinydb import TinyDB, Query
db = TinyDB('db.json')
feed_table = db.table('feed')
article_table = db.table('article')
from tinydb.table import Document
import threading

lock = threading.Lock()

def id_to_str(f):
    f["id"] = str(f["id"])
    return f

# note that tinydb doesnt do documentid as string, so conversion is done here
def get_feeds() -> list[RSSFeed]:
    all_feeds = feed_table.all()
    return [RSSFeed(**f) for f in all_feeds]

def get_articles() -> list[RSSArticle]:
    all_articles = article_table.all()
    return [RSSArticle(**f) for f in all_articles]

def feed_exists(feed_id) -> bool:
    return feed_table.contains(doc_id=int(feed_id))

def create_feed(feed, feed_id) -> str:  
    with lock:
        return str(feed_table.insert(Document(feed, doc_id=int(feed_id))))

def get_feed(feed_id) -> RSSFeed:
    print("finding", feed_id)
    if (feed_table.contains(doc_id=int(feed_id))):
        s = feed_table.get(doc_id=int(feed_id))
        print(s),
        return id_to_str(s)
    return None

def update_feed(feed_id, edit) -> bool:
    with lock:
        if (feed_table.contains(doc_id=int(feed_id))):
            feed_table.update(edit, doc_ids=[int(feed_id)])
            return True
    return False

def delete_feed(feed_id) -> bool:
    with lock:
        if (feed_table.contains(doc_id=int(feed_id))):
            feed_table.remove(doc_ids=[int(feed_id)])
            return True
    return False

def create_article(article) -> str:
    with lock:
        return str(article_table.insert(Document(article, doc_id=int(article.id))))

def article_exists(article_id) -> bool:
    return article_table.contains(doc_id=int(article_id))


def drop_articles():
    db.drop_table('article')
