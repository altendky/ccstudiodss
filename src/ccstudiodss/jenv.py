import os.path
import subprocess
import sys

import click

import ccstudiodss

jenv_path = os.path.join(
    os.path.split(os.path.dirname(ccstudiodss.__file__))[0],
    'ccstudio-dss-jenv',
)

bin_names = ('bin', 'Scripts')


def jenv_bin_path():
    for bin_name in bin_names:
        path = os.path.join(jenv_path, bin_name)
        if os.path.isdir(path):
            return path


@click.command()
@click.option('--jython', default='jython')
@click.option('--jenv-path', default=jenv_path)
@click.option('--editable', is_flag=True)
@click.option(
    '--package',
    type=str,
    default='git+https://github.com/ccstudio-dss#egg=ccstudio-dss',
)
def cli(jython, jenv_path, editable, package):
    click.echo('Creating Jython virtualenv: {}'.format(jenv_path))

    subprocess.run(
        [
            sys.executable,
            '-m', 'virtualenv',
            '-p', jython,
            jenv_path,
        ],
        check=True,
    )

    subprocess.run(
        [
            os.path.join(jenv_bin_path(), 'pip'),
            'install',
            *(['-e'] if editable else []),
            package,
        ],
        check=True,
    )
