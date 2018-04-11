import os
import pathlib
import sys

import pytest

import ccstudiodss.api


class BasePathError(Exception):
    pass


@pytest.fixture
def ccstudiodss_session(pytestconfig):
    ccxml = pytestconfig.getoption('ccxml')

    with ccstudiodss.api.Session(ccxml=ccxml) as session:
        yield session


def pytest_addoption(parser):
    group = parser.getgroup('ccstudiodss')

    group.addoption('--ccs-base-path')
    group.addoption('--ccxml', required=True)


def pytest_configure(config):
    base_path = config.getoption('ccs_base_path')

    if base_path is None:
        base_path = find_base_path()

    ccstudiodss.api.add_jars(base_path=base_path)


versions = (8, 7, 6, 5)

linux_base_paths = tuple(
    pathlib.Path(path)
    for path in (
        *(
            pathlib.Path(os.sep)/'opt'/'ti'/'ccsv{}'.format(version)/'ccs_base'
            for version in versions
        ),
        *(
            pathlib.Path.home()/'ti'/'ccsv{}'.format(version)/'ccs_base'
            for version in versions
        ),
    )
)

windows_base_paths = tuple(
    pathlib.Path(path)
    for path in (
        *(
            pathlib.Path('c:')/os.sep/'ti'/'ccsv{}'.format(version)/'ccs_base'
            for version in (8, 7, 6, 5)
        ),
    )
)

base_paths = {
    'linux': linux_base_paths,
    'win32': windows_base_paths,
}[sys.platform]


def find_base_path():
    for path in base_paths:
        if path.is_dir():
            return path

    raise BasePathError('Unable to find base path in: {}'.format(
        ', '.join(repr(str(path)) for path in base_paths),
    ))
