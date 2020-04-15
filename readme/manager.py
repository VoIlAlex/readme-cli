import os
import requests
import datetime
import getpass
import readme.config as cfg
from loguru import logger
from typing import List


def list_readmes() -> List[str]:
    readmes = []
    for attr in dir(cfg):
        if attr.startswith('README_TEMPLATE_') and attr.endswith('_URL'):
            readme_name = attr.split('_')[-2].lower()
            readmes.append(readme_name)
    return readmes


def fetch_readme(readme_name: str) -> str:
    readme_url_name = f'README_TEMPLATE_{readme_name.upper()}_URL'
    readme_url = getattr(cfg, readme_url_name)
    response = requests.get(readme_url)
    readme_content = response.text
    return readme_content


class ReadmeManager:
    def __init__(self, readmes_folder: str = None):
        self.readmes_folder = readmes_folder

    def update(self):
        if self.readmes_folder is None:
            logger.error('Failed to update. READMEs folder is not specified.')
            return
        
        for readme_name in list_readmes():
            readme_content = fetch_readme(readme_name)
            readme_path = os.path.join(self.readmes_folder, readme_name)
            with open(readme_path, 'w+') as f:
                f.write(readme_content)

    def __fill_missed_kwargs(self, kwargs: dict):
        not_or_none = lambda x: x not in kwargs or kwargs[x] is None
        if not_or_none('license_name'):
            kwargs['license_name'] = 'LICENSE.md'
        if not_or_none('project_description'):
            kwargs['project_description'] = 'Short description goes here.'
        if not_or_none('author_fullname'):
            kwargs['author_fullname'] = getpass.getuser()
        if not_or_none('author_nickname'):
            kwargs['author_nickname'] = 'voilalex'
        return kwargs

    def get(self, readme_name: str, project_name: str, local_only: bool = False, **kwargs):
        kwargs = self.__fill_missed_kwargs(kwargs)
        if self.readmes_folder is None:
            if local_only:
                raise FileNotFoundError('License could not be found.')
            return fetch_readme(readme_name)
        else:
            readme_path = os.path.join(self.readmes_folder, readme_name)
            if os.path.exists(readme_path):
                with open(readme_path) as f:
                    readme_content = ''.join(f.readlines())
                readme_content = readme_content.format(
                    project_name=project_name,
                    **kwargs
                )
                return readme_content
            elif local_only:
                raise FileNotFoundError('License could not be found.')
            else:
                self.update()
                return self.get(readme_name, project_name=project_name, local_only=True)
