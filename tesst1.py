# coding: utf-8
import json

# with open("user_info_test.txt", "r") as fr:
with open("users_trial.info", "r",encoding='utf-8') as fr:
    data = fr.readlines()
    print(len(data))
fw = open("user.location", "w",encoding='utf-8')
for line in data:
    dic = json.loads(line)
    screen_name = dic.get('screen_name', '')
    location = dic.get('location', '')
    record = '%s\t%s\n' % (screen_name, location)
    # print(record)
    fw.write(record)
fw.close()