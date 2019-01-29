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
            return {'default': ccstudiodss.utils.fspath(found[0])}
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


def create_target_option(default=None):
    return click.option(
        '--target',
        default=default,
        required=default is None,
        show_default=True,
    )



def create_build_command(default_target=None):
    @click.command()
    @create_target_option(default=default_target)
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

    return build


cli.add_command(create_build_command())


def create_ccxml_option(project_name, project_root=None):
    variable_name = '{}_CCXML'.format(project_name.upper())

    if project_root is None:
        project_root = pathlib.Path.cwd()

    paths = list(project_root.glob('*.ccxml'))
    if len(paths) == 1:
        default_or_required = {'default': paths[0]}
    else:
        default_or_required = {'required': True}
        
    ccxml_option = click.option(
        '--ccxml',
        type=click.Path(exists=True, dir_okay=False),
        envvar=variable_name,
        **default_or_required,
        help='.ccxml device configuration file (${})'.format(variable_name),
        show_default=True,
        )

    return ccxml_option


def create_binary_option(project_name, required=False):
    variable_name = '{}_BINARY'.format(project_name.upper())

    return click.option(
        '--embedded-binary', '--binary', 'binary',
        type=click.Path(exists=True, dir_okay=False, resolve_path=True),
        envvar=variable_name,
        help='.out embedded binary file (${})'.format(variable_name),
        show_default=True,
        required=required,
    )


binary_option = create_binary_option(project_name='dss')


def create_load_command(project_name, project_root=None):
    @cli.command()
    @create_binary_option(project_name=project_name)
    @create_ccxml_option(project_name=project_name, project_root=project_root)
    @ccs_base_path_option
    def load(binary, ccxml, ccs_base_path):
        ccstudiodss.api.add_jars(base_path=ccs_base_path)

        with ccstudiodss.api.Session(ccxml=ccxml) as session:
            session.load(binary=binary)
            session.run()

    return load


cli.add_command(
    create_load_command(
        project_name='dss',
    ),
    name='load',
)
