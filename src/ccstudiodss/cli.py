import os
import pathlib
import webbrowser

import click

import ccstudiodss.api
import ccstudiodss.utils


DSS_PROJECT_ROOT = 'DSS_PROJECT_ROOT'
project_root_option = click.option(
    '--project-root',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    envvar=DSS_PROJECT_ROOT,
    required=True,
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


def default_base_path():
    base_path = ccstudiodss.utils.find_base_path()
    if base_path is None:
        return {'required': True}
    
    return {'default': base_path}

ccs_base_path_option = click.option(
    '--ccs-base-path',
    type=click.Path(exists=True, file_okay=False),
    show_default=True,
    **default_base_path(),
    help='CCS base directory, e.g. /ti/ccsv8/ccs_base'
)


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


# https://github.com/pallets/click/issues/605#issuecomment-277539425
class EnumType(click.Choice):
    def __init__(self, enum):
        choices = [e.name for e in enum]
        print('choices', choices)
        super().__init__(choices)
        self.enum = enum

    def convert(self, value, param, ctx):
        return self.enum[super().convert(value, param, ctx)]


build_type_option = click.option(
    '--build-type',
    type=EnumType(ccstudiodss.api.BuildTypes),
    default=ccstudiodss.api.BuildTypes.incremental.name,
    show_default=True,
)


target_option = click.option('--target', required=True)


@cli.command()
@target_option
@build_type_option
@project_root_option
@project_name_option
def build(target, build_type, project_root, project_name):
    """Build the project using Code Composer Studio
    """
    ccstudiodss.api.build(
        target=target, 
        build_type=build_type,
        project_root=project_root,
        project_name=project_name,
    )


GRIDTIED_CCXML = 'GRIDTIED_CCXML'

def create_ccxml_option(project_root):
    paths = list(project_root.glob('*.ccxml'))
    if len(paths) != 1:
        default_or_required = {'required': True}
    else:
        default_or_required = {'default': paths[0]}
        
    ccxml_option = click.option(
        '--ccxml',
        type=click.Path(exists=True, dir_okay=False),
        envvar=GRIDTIED_CCXML,
        **default_or_required,
        help='.ccxml device configuration file (${})'.format(GRIDTIED_CCXML),
        show_default=True,
        )

    return ccxml_option
