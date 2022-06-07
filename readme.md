# messari-rss
This is done in response to the following code challenge:
https://messari.notion.site/Coding-Challenge-Back-End-Media-01-06-22-dfd11c0d3c534fa8ac92749dae1e15a4


## Installation

```bash
pip install -r requirements.txt
```

## Usage

# run the api server
*Not for production usage
*default port served at 8000

```bash
uvicorn api:app
```

# run the processor
The processor periodically combs through all feeds every 30 secs for new articles. Note that every time a new feed is introduced, current articles from the rss xml are treated as *new*

```bash
python processor.py
```
## optional

# inject sample feeds
```bash
python init.py
```

# API docs
http://localhost:8000/docs

# Prefect UI to view processor job runs
http://localhost:4200

## More info
API server is the only one interacting with the file-based db (tinydb), to eliminate multi-client concurrency problems.
The processor communicates with API server via a set of APIs with '/processor' prefix to check article existence, add new articles etc.  This path prefix could potentially be secured if needed :)


