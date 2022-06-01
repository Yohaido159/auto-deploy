from itertools import filterfalse
import os
import tempfile
from pprint import pprint
from pathlib import Path
from typing import Tuple
import zipfile
import os
from pathlib import Path
import subprocess

from uritemplate import variables

from config.parse_file_variables import parse_file_inplace
from event.event_logger import event_logger


def from_st_size_to_kb(size):
    return int(size) / 1024


# class ZipCreator:
#     def __init__(self, folder_path, zip_path, excludes_files, excludes_folders, limit_size):
#         self.folder_path = folder_path
#         self.zip_path = zip_path
#         self.excludes_files = excludes_files
#         self.excludes_folders = excludes_folders
#         self.limit_size = limit_size
#         self.zipfile_array: Tuple[zipfile.ZipFile,  float] = []

#     def create_zip(self):
#         self.zip_file = zipfile.ZipFile(
#             self.zip_path, 'w', zipfile.ZIP_DEFLATED)
#         self.folder_path = Path(self.folder_path)
#         self.zip_file_size = 0
#         self.zip_file_size += self.add_folder(self.folder_path)
#         self.zip_file.close()

#     def add_folder(self, folder_path):
#         folder_path = Path(folder_path)
#         if folder_path.name in self.excludes_folders:
#             return 0

#         folder_size = 0
#         for child in folder_path.iterdir():
#             if child.is_dir():
#                 folder_size += self.add_folder(child)
#             elif child.is_file():
#                 folder_size += self.add_file(child)
#         return folder_size

#     def add_file(self, file_path):
#         file_path = Path(file_path)
#         if file_path.name in self.excludes_files:
#             return 0
#         else:
#             # file_size = file_path.stat().st_size
#             file_size = self.get_compresses_file_size_with_tmp_zipfile(
#                 file_path)
#             self.zip_file_size += file_size
#             self.zip_file.write(str(file_path), str(
#                 file_path.relative_to(self.folder_path)))
#             return file_size

#     def check_zip_size(self):
#         print("self.zip_file_size", self.zip_file_size)
#         if self.zip_file_size > self.limit_size:
#             return True
#         else:
#             return False

#     def create_second_zip(self):
#         self.second_zip_file = zipfile.ZipFile(
#             self.zip_path.replace('.zip', '_2.zip'), 'w', zipfile.ZIP_DEFLATED)
#         self.second_zip_file_size = 0

#     @staticmethod
#     def get_compresses_file_size_with_tmp_zipfile(file_path):
#         with tempfile.TemporaryDirectory() as tmpdirname:
#             tmp_zip_path = os.path.join(tmpdirname, 'tmp.zip')
#             with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as tmp_zipfile:
#                 tmp_zipfile.write(file_path, os.path.basename(file_path))
#             return os.path.getsize(tmp_zip_path)

class ZipCheck:
    def __init__(self, root_folder, limit_size, excludes_files, excludes_folders, zip_path
                 ):
        self.root_folder = Path(root_folder)
        self.limit_size = limit_size
        self.zip_path = zip_path
        self.excludes_files = excludes_files
        self.excludes_folders = excludes_folders
        self.idx = 0

    def check_folder_size(self, folder_path):
        folder_path = Path(folder_path)
        folder_size = 0
        if folder_path.name in self.excludes_folders:
            return 0
        for child in folder_path.iterdir():
            if child.is_dir():
                folder_size += self.check_folder_size(child)
            elif child.is_file():
                folder_size += self.calc_file(child)

        print("folder_size", folder_size)
        print("self.limit_size", self.limit_size)
        if folder_size > self.limit_size:
            raise Exception(
                f"Folder {folder_path} size {folder_size} is bigger than limit {self.limit_size}")
        return folder_size

    def calc_file(self, file_path):
        file_path = Path(file_path)
        if file_path.name in self.excludes_files:
            return 0
        else:
            file_size = self.get_compressed_size(
                file_path)
        if file_size > self.limit_size:
            raise Exception(
                f"File {file_path} size {file_size} is bigger than limit {self.limit_size}")
        return file_size

    def get_compressed_size(self, file_path):
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_zip_path = os.path.join(tmpdirname, 'tmp.zip')
            with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as tmp_zipfile:
                tmp_zipfile.write(file_path, os.path.basename(file_path))
            return os.path.getsize(tmp_zip_path)

    def create_zip(self, base_items_in_dirs):

        zip_file = self.create_zipfile(self.idx)
        global_size = 0

        for base_item, is_added in base_items_in_dirs.items():
            if is_added == 'added':
                continue
            # is_added = 'added'

            size = 0
            if base_item.is_dir():
                size += self.check_folder_size(base_item)
            elif base_item.is_file():
                size += self.calc_file(base_item)
            global_size += size

            if global_size > self.limit_size:
                self.idx += 1
                self.create_zip(base_items_in_dirs)
            else:
                base_items_in_dirs[base_item] = 'added'
                self.add_item_to_zip(zip_file, base_item)
        print("global_size", global_size)
        zip_file.close()

    def add_item_to_zip(self, zipfile, item):
        if item.is_dir():
            if item.name in self.excludes_folders:
                return
            for child in item.iterdir():
                self.add_item_to_zip(zipfile, child)
        elif item.is_file():
            if item.name in self.excludes_files:
                return

            zipfile.write(str(item), str(item.relative_to(self.root_folder)))

    def create_zipfile(self, idx):
        return zipfile.ZipFile(
            f'{self.zip_path}_{idx}.zip', 'w', zipfile.ZIP_DEFLATED)

    def to_kb(self, size):
        return f'{size / 1024:.2f} KB'


@ event_logger
def handle_lambda_zip(folder_path, zip_path):
    try:
        os.remove(zip_path)
    except OSError:
        pass

    gitgnore_file = Path(folder_path) / '.gitignore'
    gitgnore_content = gitgnore_file.read_text().split('\n')
    gitgnore_file_content = filter(
        lambda f: not f.endswith('/'), gitgnore_content)
    gitgnore_folder_content = map(lambda f: f.replace(
        '/', ''), filter(lambda f: f.endswith('/'), gitgnore_content))

    gitgnore_file_content = list(gitgnore_file_content)
    gitgnore_folder_content = list(gitgnore_folder_content)

    create_zip_file(folder_path=folder_path, zip_path=zip_path, excludes_files=gitgnore_file_content,
                    excludes_folders=gitgnore_folder_content, limit_size=50 * 1024 * 1024)


@ event_logger
def create_zip_file(folder_path, zip_path, excludes_files, excludes_folders, limit_size):
    print("limit_size", limit_size)

    zip_creator = ZipCheck(
        root_folder=folder_path, limit_size=limit_size, excludes_files=excludes_files, excludes_folders=excludes_folders, zip_path=zip_path)
    base_items_in_dirs = {item: 'not_added' for item in list(
        zip_creator.root_folder.iterdir())}
    zip_size = zip_creator.create_zip(base_items_in_dirs)

    print("zip_size", zip_size)

    return zip_path

    # with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    #     cwd = os.getcwd()
    #     os.chdir(folder_path)
    #     for root, dirs, files in os.walk('.'):
    #         if any(folder in root for folder in excludes_folders):
    #             continue

    #         for file in files:
    #             if file in excludes_files:
    #                 continue

    #             file_path = os.path.join(root, file)
    #             zip_file.write(file_path)
    #     os.chdir(cwd)


@ event_logger
def handle_lambda_layer_zip(lambda_layer_zip_path, generated_files, project_name):

    parse_file_inplace(file_path=Path(generated_files) / 'Dockerfile_base',
                       variables={'project_name': project_name},
                       new_name='Dockerfile')

    subprocess.run(['rm', f'{lambda_layer_zip_path}'])
    subprocess.run(['docker', 'rm', 'deps-wrap'])
    subprocess.run(['docker', 'build', '-t', 'deps', generated_files])
    subprocess.run(['docker', 'run', '--name', 'deps-wrap', 'deps', ])
    subprocess.run(
        ['docker', 'cp', f'deps-wrap:app/python/lib/python3.8/site-packages/', f'{generated_files}/python/lib/python3.8/'])
    # subprocess.run(
    #     ['docker', 'cp', f'deps-wrap:app/{project_name}-lambda-layer.zip', f'{generated_files}'])
    create_zip_file(folder_path=Path(
        r'C:\projects\utils\auto-deploy\generated_files\python\lib\python3.8\site-packages'
    ), zip_path=lambda_layer_zip_path, excludes_files=[],
        excludes_folders=[
            'boto3',
            'botocore',
    ], limit_size=30 * 1024 * 1024)


def from_mermed_to_class(self):
    """
    root_folder --> create_file --> loop_folder--> calc_size -->
        checksize{biger then limit} -->|No| add_folder --> loop_folder
        checksize{biger then limit} -->|Yes| create_file
    """
