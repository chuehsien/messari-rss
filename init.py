import requests
urls = [
"https://decrypt.co/feed",
"https://blockworks.co/feed",
"https://cryptopotato.com/feed",
"https://cryptobriefing.com/feed",
"https://dailyhodl.com/feed",
"https://cointelegraph.com/rss",

]

for u in urls:
    r = requests.post("http://localhost:8000/feed", json={"url": u, "pattern":"((hack)|(exploit)|(vuln)|(Ethereum)|(ETH)|(fork)|(upgrad))"})



# ids = [
#     "30489518063111339506858504329274680525",
#     "173264338435901227362578033734916122108",
#     "212190998768564815257994798270902994007",
#     "194584136110742833164887664173213719692",
#     "119093869184133879150074639699893029268",
#     "48800812630069758117699321407296994883"
# ]
# for i in ids:
#     r = requests.post(f"http://localhost:8000/feed/{i}", json={"pattern":".*"})
