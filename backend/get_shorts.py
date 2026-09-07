import urllib.request
import re

queries = ["food+shorts", "cooking+shorts", "recipe+shorts", "street+food+shorts", "pizza+shorts", "burger+shorts", "indian+food+shorts", "dessert+shorts"]
ids = set()

for q in queries:
    try:
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={q}").read().decode()
        matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        ids.update(matches)
        if len(ids) > 60:
            break
    except:
        pass

print(list(ids)[:60])
