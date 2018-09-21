import os
import pathlib
import webbrowser

import click

import ccstudiodss.api
import ccstudiodss.utils
import ccstudiodss.build


@click.group()
def cli():
    pass


def default_ccxml():
    cwd = pathlib.Path().resolve()
    for path in [cwd, *cwd.parents]:
        found = tuple(path.glob('*.ccxml'))

        if len(found) == 1:
            return {'default': str(found[0])}
        elif len(found) > 1:
            break

    return {'required': True}


ccxml_option = click.option(
    '--ccxml',
    type=click.Path(exists=True, dir_okay=False),
    show_default=True,
    **default_ccxml(),
)

ccs_base_path_option = click.option(
    '--ccs-base-path',
    type=click.Path(exists=True, file_okay=False),
)


@cli.command()
@click.option(
    '--binary',
    type=click.Path(exists=True, dir_okay=False),
    required=True,
)
@ccxml_option
@ccs_base_path_option
def load(binary, ccxml, ccs_base_path):
    ccstudiodss.api.add_jars(base_path=ccs_base_path)

    with ccstudiodss.api.Session(ccxml=ccxml) as session:
        session.load(binary=binary)
        session.run()


@cli.command()
@ccxml_option
@ccs_base_path_option
def restart(ccxml, ccs_base_path):
    ccstudiodss.api.add_jars(base_path=ccs_base_path)

    with ccstudiodss.api.Session(ccxml=ccxml) as session:
        session.restart()


@cli.command()
@ccs_base_path_option
@click.option('--open/--show', 'open_', default=True)
def docs(ccs_base_path, open_):
    if ccs_base_path is None:
        ccs_base_path = ccstudiodss.utils.find_base_path()

    path = os.fspath(
            ccs_base_path / 'scripting' / 'docs' / 'GettingStarted.htm',
        )

    if open_:
        webbrowser.open(path)
    else:
        click.echo(path)


cli.add_command(ccstudiodss.build.cli, name='build')
