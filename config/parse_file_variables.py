

import os
from click import Path


def parse_file_and_return_str(file_path,  variables: dict):

    with open(file_path, 'r') as f:
        content = f.read()
    for key, value in variables.items():
        content = content.replace("{{"+key+"}}", value)
    return content


def parse_file_inplace(file_path,  variables: dict, new_name=None):
    with open(file_path, 'r') as f:
        content = f.read()
    for key, value in variables.items():
        content = content.replace("{{"+key+"}}", value)
    if new_name:
        with open(os.path.join('generated_files', new_name), 'w') as f:
            f.write(content)
    else:
        with open(file_path, 'w') as f:
            f.write(content)
