import click
import os
from readme.manager import ReadmeManager
from appdata import AppDataPaths
from loguru import logger


@click.command()
@click.argument('readme-variant', type=click.Choice(['small', 'medium', 'large']), default='medium')
@click.option('-p', '--print', 'print_', is_flag=True)
@click.option('-n', '--name', default=os.path.split(os.getcwd())[-1])
@click.option('-d', '--description', required=False)
@click.option('-f', '--fullname', required=False)
@click.option('-k', '--nickname', required=False)
@click.option('-l', '--license', required=False)
def cli(readme_variant, print_, name, description, fullname, nickname, license):
    app_data_paths = AppDataPaths(
        app_name='readme',
        root_appdata='.opensource',
        with_dot=False
    )
    if app_data_paths.require_setup():
        app_data_paths.setup()

    readmes_folder = app_data_paths.join('reamdes')
    if not os.path.exists(readmes_folder):
        os.makedirs(readmes_folder)

    manager = ReadmeManager(
        readmes_folder=readmes_folder
    )
    try:
        readme_content = manager.get(
            readme_variant, 
            project_name=name,
            project_description=description,
            author_fullname=fullname,
            author_nickname=nickname,
            license_name=license
        )
    except FileNotFoundError:
        logger.error('Cannot find the specified readme.')
        exit(-1)
    if print_:
        print(readme_content)
    else:
        with open('./README.md', 'w+') as f:
            f.write(readme_content)
