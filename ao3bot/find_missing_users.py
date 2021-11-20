import json

with open("user_bookmarks_clean.json", "r") as f:
    clean_list = json.load(f)

with open("user_bookmarks.json", "r") as f:
    unclean_list = json.load(f)

clean_users = list(map(lambda x: x.get("user"), clean_list))

unclean_users = list(map(lambda x: x.get("user"), unclean_list))

missing_users = []

for user in unclean_users:
    if user not in clean_users:
        missing_users.append(user)
data_to_insert = []
for i in range(len(unclean_list)):
    for missing_user in missing_users:
        if unclean_list[i]["user"] == missing_user:
            data_to_insert.append(unclean_list[i])

with open("missing_user_bookmarks.json", "w") as f:
    json.dump(data_to_insert, f, indent = 6)
