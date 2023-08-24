import json
import os
import sys

config_file_path = sys.argv[1]
print('file:', config_file_path)

with open(config_file_path) as f:
    config = json.loads(f.read())

replace_set = {}

for obj in config['organizations'].values():
    for user in obj['users'].values():

        file_path = os.path.join('..', user['private_key'])

        if not os.path.isfile(file_path):
            dir_path = os.path.dirname(file_path)

            if not os.path.exists(dir_path):
                raise RuntimeError(dir_path)

            dir_content = os.listdir(dir_path)
            if len(dir_content) != 1:
                raise RuntimeError(dir_path, dir_content)

            new_file_name = dir_content[0]
            old_file_name = os.path.basename(file_path)

            replace_set[old_file_name] = new_file_name

for k, v in replace_set.items():
    print(k, '->', v)

if not replace_set:
    print('already up-to-date!')

with open(config_file_path) as f:
    config_as_string = f.read()

for k, v in replace_set.items():
    config_as_string = config_as_string.replace(k, v)

with open(config_file_path, 'w') as f:
    f.write(config_as_string)
