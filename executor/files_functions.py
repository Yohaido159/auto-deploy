import re
import os
from pathlib import Path
import subprocess
from subprocess import check_output

from event.event_logger import event_logger


@event_logger
def build_react(react_path, output_folder_name):
    react_path = Path(react_path)
    cwd = os.getcwd()
    os.chdir(react_path)
    os.environ['BUILD_PATH'] = f'{cwd}/generated_files/{output_folder_name}'
    os.system(f"npm run build")
    os.chdir(cwd)


@event_logger
def handle_create_requirements(pip_path, generated_files):
    pip_path = Path(pip_path)
    freeze_raw = check_output(
        [pip_path, 'freeze'], shell=True, universal_newlines=True)
    freeze_raw = re.sub('(boto.+|django-tenants.+|psycopg2.+)', '', freeze_raw)
    freeze_raw = freeze_raw.split('\n')

    with open(f'{generated_files}/requirements.txt', 'w') as f:
        f.write('\n'.join(sorted(freeze_raw)))


@event_logger
def insert_packages_into_zip(pip_path, utils_path, generated_files, project_name):
    pip_path = Path(pip_path)
    utils_path = Path(utils_path)

    abs_current_path = os.getcwd()
    os.chdir(utils_path / 'django-tenants')
    subprocess.run([
        pip_path,
        'install',
        '.',
        '-t',
        f'{abs_current_path}/{generated_files}/python/lib/python3.8/site-packages/',
        '--no-deps',
        '--upgrade'
    ])

    os.chdir(f'{abs_current_path}/generated_files/')
    # os.system('powershell ls')
    subprocess.run(
        ['zip', '-r', f'{project_name}-lambda-layer.zip', f'./python/lib/python3.8/site-packages/', ])
    os.chdir(abs_current_path)


@event_logger
def exclude_packages_from_zip(pip_path, utils_path, generated_files, project_name):
    ...
    # subprocess.run(
    #     ['zip', '-r', f'{project_name}-lambda-layer.zip', f'./python/lib/python3.8/site-packages/', ])
