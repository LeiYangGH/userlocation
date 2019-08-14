# coding: utf-8
import json
import os

def extract_user_city(input_file="users_trial.info", output_file="user.location"):
    if os.path.isfile(output_file):
        return #already exits so skip creating
    with open(input_file, "r", encoding='utf-8') as fr:
        data = fr.readlines()
        print(len(data))
    fw = open(output_file, "w", encoding='utf-8')
    for line in data:
        dic = json.loads(line)
        screen_name = dic.get('screen_name', '')
        location = dic.get('location', '')
        record = '%s\t%s\n' % (screen_name, location)
        # print(record)
        fw.write(record)
    fw.close()
