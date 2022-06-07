import hashlib
from datetime import datetime
pubdate_dt_format = '%a, %d %b %Y %H:%M:%S %z'
dt_format = '%Y %d-%m %H:%M:%S'


def shorten_body(s, length=77):
    if (len(s) >= length):
        return f"{s[:length]}..."
    return s


# article methods
def makeId(feed_id,article_title):
    s = f"{feed_id}_{article_title}"
    hash_object = hashlib.md5(s.encode())
    return str(int(hash_object.hexdigest(), 16))

def getTimestampFromRaw(raw):
    return datetime.strptime(raw.pubDate.text, pubdate_dt_format).timestamp()

def getTitleFromRaw(raw):
    return raw.title.text

def getDescFromRaw(raw):
    return raw.description.text

def getLinkFromRaw(raw):
    return raw.link.text

# feed methods
def makeFeedId(url,pattern):
    s = f"{url}_{str(pattern) if pattern is not None else '*'}"
    print("Hashing", s)
    hash_object = hashlib.md5(s.encode())
    return str(int(hash_object.hexdigest(), 16))

        # self.articles_dicts = [{'title':a.find('title').text,'link':a.link.next_sibling.replace('\n','').replace('\t',''),'description':a.find('description').text,'pubDate':a.find('pubDate').text} for a in self.articles]
