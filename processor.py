import os

os.environ.setdefault('PREFECT_LOGGING_LEVEL', 'ERROR')

from utils import getTimestampFromRaw, getTitleFromRaw, getDescFromRaw, getLinkFromRaw
from bs4 import BeautifulSoup
import requests
import datetime
import re
from RSSArticle import RSSArticle
import time
import internal_api_helper
from prefect import flow, task
import schedule

get_feed_url="http://localhost:8000/feed"
interval_secs = 30
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53'
}
dt_format = '%Y %d-%m %H:%M:%S'
pubdate_dt_format = '%a, %d %b %Y %H:%M:%S %z'

@task
def process_article(feed_id, pattern, _article):
    # check patterns
    matched = False
    if (matchPattern(_article["title"],pattern)):
        matched = True
    if (not matched and matchPattern(_article["description"],pattern)):
        matched = True
    if (not matched and matchPattern(_article["link"],pattern)):
        matched = True

    # try to go to website to match
    if (not matched and _article["link"] is not None):
        try:
            web_content = requests.get(_article["link"])
            soup = BeautifulSoup(web_content.text,'html.parser')
            if(matchPattern(soup.get_text(), pattern)):
                matched = True
        except:
            print(f"Error scrapping: {_article['link']}")

    if (not matched):
        return None

    article = RSSArticle(feed_id=feed_id, timestamp=_article["timestamp"],title=_article["title"],description=_article["description"], link=_article["link"])
    if (not internal_api_helper.article_exist(article.id)):
        internal_api_helper.new_article(article)
        # print(f"Created article: {article.id}")
        print(f"===============New article===============")
        article.print_info()
        print(f"=========================================")

    else:
        # print(f"Article exists: {article.id}")
        pass
    return article.id

def matchPattern(text, pattern):
    if (pattern is None):
        return True
    test = re.search(pattern, text)
    return (test is not None)

@task
def fetch_feed(feed):
    hdr = headers
    ifModifiedSince = feed["lastBuildTimestamp"] if ("lastBuildTimestamp" in feed) else None
    if (not feed["forceRefresh"] and ifModifiedSince is not None):
        d = datetime.datetime.utcfromtimestamp(ifModifiedSince)
        hdr = {'User-Agent': headers["User-Agent"], "If-Modified-Since": d.strftime('%a, %d %b %Y %H:%M:%S GMT')}
        
    r = requests.get(feed["url"], headers=hdr)
    
    status_code = r.status_code
    if (status_code == 304):
        # print(f"{feed['url']} 304: No need articles")
        return None
    elif (status_code == 200):
        raw = BeautifulSoup(r.text, features="xml")
        newBuildTimestamp = int(datetime.datetime.strptime(raw.lastBuildDate.text, pubdate_dt_format).timestamp())

        if (not feed["forceRefresh"] and ifModifiedSince is not None and ifModifiedSince == newBuildTimestamp):
            # print(f"{feed['url']}: Skipping as no new build since", ifModifiedSince)
            return None
        else:
            # extract useful stuff
            articles = [{
                "timestamp": getTimestampFromRaw(_a),
                "title":getTitleFromRaw(_a),
                "description":getDescFromRaw(_a),
                "link":getLinkFromRaw(_a),
            } for _a in raw.findAll('item')]

            result = {
                "lastBuildTimestamp": int(datetime.datetime.strptime(raw.lastBuildDate.text, pubdate_dt_format).timestamp()),
                "articles": articles
                # [a for a in articles if 
                #     (
                #         matchPattern(a["title"],feed["pattern"]) or 
                #         matchPattern(a["description"],feed["pattern"]) or 
                #         matchPattern(a["link"],feed["pattern"])
                #     )
                # ]
            }
            return result


    else:
        return None

# output is an 
# @task
# def one_rss(feed):
#     raw = fetch_feed(feed)
#     if (raw is not None):
        
#         articles = raw.findAll('item')
        
#         # use prefect for this to parallelize
#         _article_ids = [process_article(feed["id"], _article) for _article in articles]
#         article_ids = [r.result() for r in _article_ids]
       
#         feed["lastBuildTimestamp"] = int(datetime.datetime.strptime(raw.lastBuildDate.text, pubdate_dt_format).timestamp())
#         feed["lastResult"] = ",".join(article_ids)

    
#     feed["lastQueriedTimestamp"] = int(time.time())
#     internal_api_helper.processed_feed(feed)
#     return feed

@task(retries=5, retry_delay_seconds=10)
def update_feed(feed):
    internal_api_helper.processed_feed(feed)

@task(retries=5, retry_delay_seconds=10)
def get_all_feeds():
    r = requests.get(get_feed_url)
    r = r.json()
    return r
@flow
def do_one_pass():
    runtime = datetime.datetime.now()
    # print(f"Running at {runtime.strftime(pubdate_dt_format)}")
    r = get_all_feeds().result()
    # fetch each feed
    _feed_results = [fetch_feed(feed) for feed in r]
    feed_results = [_r.result() for _r in _feed_results]

    # print(feed_results)
    # run through articles in each feed
    all_results = {}
    for i in range(len(r)):
        feed = r[i]
        fr = feed_results[i]
        if (fr is not None):
            articles = fr["articles"]
            all_results[feed["id"]] = [process_article(feed["id"], feed["pattern"] if "pattern" in feed else None, _article) for _article in articles]

    # now i have collate the article ids of each feed in this update.
    for i in range(len(r)):
        feed = r[i]
        fr = feed_results[i]
        if (fr is not None):
            processed_ids = [_r.result() for _r in all_results[feed["id"]]]
            processed_ids = [p for p in processed_ids if p is not None]
            feed["lastBuildTimestamp"] = fr["lastBuildTimestamp"]
            feed["lastResult"] = ",".join(processed_ids)
        feed["lastQueriedTimestamp"] = int(time.time())
        feed["forceRefresh"] = False
        update_feed(feed)

    # runtime = datetime.datetime.now()
    # print(f"Done at {runtime.strftime(pubdate_dt_format)}")

if __name__ == '__main__':
    do_one_pass()
    # time.sleep(10)
    print(f"Starting monitoring loop, runs every {interval_secs} secs")
    schedule.every(interval_secs).seconds.do(do_one_pass)
    
    while True:
        schedule.run_pending()
        time.sleep(1)