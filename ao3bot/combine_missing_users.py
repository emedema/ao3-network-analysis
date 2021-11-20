import json

with open("user_bookmarks_clean.json", "r") as f:
    clean_list = json.load(f)

with open("missing_user_bookmarks.json", "r") as f:
    missing_list = json.load(f)


final = []
for i in range(len(clean_list)):
    final.append(clean_list[i])

for i in range(len(missing_list)):
    final.append(missing_list[i])

with open("user_bookmarks_final.json", "w") as f:
    json.dump(final, f)