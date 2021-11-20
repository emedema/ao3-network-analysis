
import json
from collections import OrderedDict
with open("pop_fandoms.json", "r") as f:
    temp_list = json.load(f)

    mem = []
    final = []

    for record in temp_list:
        url = record["fandom_link"]
        if url not in mem:
            mem.append(url)
            final.append({"fandom": record["fandom"], "fandom_link": record["fandom_link"]})

with open("pop_fandoms_clean.json", "w") as f:
    json.dump(final, f, indent = 6)