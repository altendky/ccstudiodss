import os
import subprocess
import tempfile

import click

import ccstudiodss.utils


build_type_choices = ('incremental', 'full', 'clean')

DSS_PROJECT_ROOT = 'DSS_PROJECT_ROOT'
project_root_option = click.option(
    '--project-root',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    envvar=DSS_PROJECT_ROOT,
    help=(
         'Directory containing the .project file'
         ' (${})'.format(DSS_PROJECT_ROOT)
    ),
)


DSS_PROJECT_NAME = 'DSS_PROJECT_NAME'
project_name_option = click.option(
    '--project-name',
    type=str,
    envvar=DSS_PROJECT_NAME,
    help=(
         'Project name used for build artifacts'
         ' (${})'.format(DSS_PROJECT_NAME)
    ),
)


@click.command()
@click.option('--target', required=True)
@click.option(
    '--build-type',
    type=click.Choice(build_type_choices),
    default=build_type_choices[0],
    show_default=True,
)
@project_root_option
@project_name_option
def cli(target, build_type, project_root, project_name):
    """Build the project using Code Composer Studio
    """
    if project_name is None:
        project_name = pathlib.Path(project_root).parts[-1]

    with tempfile.TemporaryDirectory() as d:
        base_command = (
            os.fspath(ccstudiodss.utils.find_executable()),
            '-noSplash',
            '-data', d,
        )

        try:
            subprocess.run(
                [
                    *base_command,
                    '-application', 'com.ti.ccstudio.apps.projectImport',
                    '-ccs.location', str(project_root),
                    '-ccs.renameTo', project_name,
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            pass

        for this_build_type in (build_type, 'incremental'):
            completed_process = subprocess.run(
                [
                    *base_command,
                    '-application', 'com.ti.ccstudio.apps.projectBuild',
                    '-ccs.projects', project_name,
                    '-ccs.configuration', target,
                    '-ccs.buildType', this_build_type,
                ],
            )

        completed_process.check_returncode()
