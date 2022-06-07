import requests
server = "http://localhost:8000"
article_exist_url = server + "/processor/exists/{}"
new_article_url = server +  "/processor/add_article"
processed_feed_url = server + "/processor/update_feed_stats"


def article_exist(article_id):
    r = requests.get(article_exist_url.format(article_id))
    return r.text == "true"

def new_article(article):
    r = requests.post(new_article_url,json=dict(article))
    return r

def processed_feed(feed):
    r = requests.post(processed_feed_url,json=dict(feed))
    return r
    