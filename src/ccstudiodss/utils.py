import hashlib
import itertools
import os
import pathlib
import sys
import tempfile


class BasePathError(Exception):
    pass


class ExecutablePathError(Exception):
    pass


fspath = getattr(os, 'fspath', str)

versions = ('920', '910', '901', '900', '8', '7', '6', '5')

linux_base_paths = (
    pathlib.Path(os.sep)/'opt'/'ti'/'ccs'/'ccs_base',
    *itertools.chain.from_iterable(
        (
            pathlib.Path(os.sep)/'opt'/'ti'/'ccsv{}'.format(version)/'ccs_base',
            pathlib.Path(os.sep)/'opt'/'ti'/'ccs{}'.format(version)/'ccs'/'ccs_base',
            pathlib.Path(os.sep)/'opt'/'ti'/'ccsv{}'.format(version)/'ccsv{}'.format(version)/'ccs_base',
            pathlib.Path.home()/'ti'/'ccsv{}'.format(version)/'ccs_base',
            pathlib.Path.home()/'ti'/'ccs{}'.format(version)/'ccs'/'ccs_base',
            pathlib.Path.home()/'ti'/'ccsv{}'.format(version)/'ccsv{}'.format(version)/'ccs_base',
        )
        for version in versions
    ),
)

windows_base_paths = tuple(itertools.chain.from_iterable(
    (
        pathlib.Path('c:') / os.sep / 'ti' / 'ccsv{}'.format(version) / 'ccs_base',
        pathlib.Path('c:') / os.sep / 'ti' / 'ccs{}'.format(version) / 'ccs' / 'ccs_base',
        # in case the ccsv8 or such gets doubled up
        pathlib.Path('c:') / os.sep / 'ti' / 'ccsv{}'.format(version) / 'ccsv{}'.format(version) / 'ccs_base',
    )
    for version in versions
))

base_paths = {
    'linux': linux_base_paths,
    'win32': windows_base_paths,
}[sys.platform]


def find_base_path():
    for path in base_paths:
        if path.is_dir():
            return path

    raise BasePathError('Unable to find base path in: {}'.format(
        ', '.join(repr(fspath(path)) for path in base_paths),
    ))


def find_executable():
    candidates = [
        find_base_path().parents[0]/'eclipse'/file_name
        for file_name in ('eclipsec.exe', 'ccstudio')
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise ExecutablePathError('Executable not found in: {}'.format(
        ', '.join(repr(fspath(candidate)) for candidate in candidates)
    ))


def generated_path_root():
    return pathlib.Path(tempfile.gettempdir())/__name__.partition('.')[0]


def generated_project_root(project_root, suffix=None):
    if suffix is None:
        suffix = ''

    hex_hash = hashlib.sha256(
        fspath(project_root).encode('utf-8'),
    ).hexdigest()

    return generated_path_root() / (hex_hash + suffix)


def generated_workspace_path(project_root, suffix=None):
     return generated_project_root(project_root, suffix=suffix) / 'workspace'

