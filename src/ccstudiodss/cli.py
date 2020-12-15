import os
import pathlib
import webbrowser

import click

import ccstudiodss.api
import ccstudiodss.utils


def create_project_root_option(
        project_name,
        default=None,
):
    variable_name = '{}_PROJECT_ROOT'.format(project_name.upper())
    return click.option(
        '--project-root',
        default=default,
        type=click.Path(exists=True, file_okay=False, resolve_path=True),
        envvar=variable_name,
        required=default is None,
        help=(
            'Directory containing the .project file'
            ' (${})'.format(variable_name)
        ),
    )


project_root_option = create_project_root_option(project_name='dss')


def create_project_name_option(project_name):
    variable_name = '{}_PROJECT_NAME'.format(project_name.upper())

    return click.option(
        '--project-name',
        type=str,
        envvar=variable_name,
        help=(
             'Project name used for build artifacts'
             ' (${})'.format(variable_name)
        ),
    )


project_name_option = create_project_name_option(project_name='dss')


def create_workspace_suffix_option(project_name):
    variable_name = '{}_WORKSPACE_SUFFIX'.format(project_name.upper())

    return click.option(
        '--workspace-suffix',
        type=str,
        envvar=variable_name,
        help=(
             'Suffix used when creating workspace such as for parallel builds in'
             ' CI (${})'.format(variable_name)
        ),
    )


workspace_suffix_option = create_workspace_suffix_option(project_name='dss')


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


def create_target_option(default=None, project_root=None):
    help = ''

    if project_root is not None:
        cproject = os.path.join(project_root, '.cproject')
        targets = ccstudiodss.api.get_cproject_targets_from_path(cproject)
        help += 'Known targets: {}'.format(', '.join(targets))

    return click.option(
        '--target',
        default=default,
        required=default is None,
        show_default=True,
        help=help,
    )


def create_targets_option(
    default=None,
    project_root=None,
    add_all=True,
):
    help = ''

    if project_root is not None:
        cproject = os.path.join(project_root, '.cproject')
        try:
            targets = ccstudiodss.api.get_cproject_targets_from_path(cproject)
        except FileNotFoundError:
            pass
        else:
            if add_all:
                targets.append('all')
            help += 'Known targets: {}'.format(', '.join(targets))

    return click.option(
        '--target',
        'targets',
        default=default,
        multiple=True,
        required=default is None,
        show_default=True,
        help=help,
    )


def create_build_command(
        project_name,
        default_targets=None,
        project_root=None,
):
    @click.command()
    @create_targets_option(
        default=default_targets,
        project_root=project_root,
        add_all=project_root is not None,
    )
    @build_type_option
    @create_project_root_option(
        project_name=project_name,
        default=project_root,
    )
    @create_project_name_option(project_name=project_name)
    @create_workspace_suffix_option(project_name=project_name)
    def build(
            targets,
            build_type,
            project_root,
            project_name,
            workspace_suffix,
    ):
        """Build the project using Code Composer Studio."""

        if workspace_suffix is not None:
            workspace_suffix = '-' + workspace_suffix

        if project_root is not None:
            project_root = pathlib.Path(project_root)

        if project_root is not None and 'all' in targets:
            targets = ccstudiodss.api.get_cproject_targets_from_path(
                path=project_root / '.cproject',
            )

        for target in targets:
            ccstudiodss.api.build(
                target=target,
                build_type=build_type,
                project_root=project_root,
                project_name=project_name,
                suffix=workspace_suffix,
            )

    return build


cli.add_command(create_build_command(project_name='dss'))


def create_list_targets_command(project_name, default_project_root=None):
    @click.command()
    @create_project_root_option(
        project_name=project_name,
        default=default_project_root,
    )
    def list_targets(
            project_root,
    ):
        """List the available project targets
        """

        if project_root is not None:
            project_root = pathlib.Path(project_root)

        targets = ccstudiodss.api.get_cproject_targets_from_path(
            path=project_root / '.cproject',
        )

        for target in targets:
            click.echo(target)

    return list_targets


cli.add_command(create_list_targets_command(project_name='dss'))


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


def create_device_pattern_option(
        project_name,
        default_pattern='.*',
        required=False,
):
    variable_name = '{}_DEVICE_PATTERN'.format(project_name.upper())

    return click.option(
        '--device-pattern', '--device', 'device_pattern',
        default=default_pattern,
        type=str,
        envvar=variable_name,
        help='Regex pattern used to select the device/core (${})'.format(
            variable_name,
        ),
        show_default=True,
        required=required,
    )


def create_timeout_option(
        project_name,
        timeout=5*60,
        required=False,
):
    variable_name = '{}_TIMEOUT'.format(project_name.upper())

    return click.option(
        '--timeout', 'timeout',
        default=timeout,
        type=str,
        envvar=variable_name,
        help='Time in seconds after which to abort (${})'.format(
            variable_name,
        ),
        show_default=True,
        required=required,
    )


def create_load_command(project_name, project_root=None, device_pattern_option=None):
    if device_pattern_option is None:
        device_pattern_option = create_device_pattern_option(project_name=project_name)

    @cli.command()
    @create_binary_option(project_name=project_name)
    @create_ccxml_option(project_name=project_name, project_root=project_root)
    @device_pattern_option
    @create_timeout_option(project_name=project_name)
    @ccs_base_path_option
    def load(binary, ccxml, device_pattern, timeout, ccs_base_path):
        """Load the project to the board."""

        ccstudiodss.api.add_jars(base_path=ccs_base_path)

        session = ccstudiodss.api.Session(
            ccxml=ccxml,
            device_pattern=device_pattern,
        )
        with session:
            session.load(binary=binary, timeout=timeout)
            session.run()

    return load


cli.add_command(
    create_load_command(
        project_name='dss',
    ),
    name='load',
)
