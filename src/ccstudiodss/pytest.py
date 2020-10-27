import pytest

import ccstudiodss.api
import ccstudiodss.utils


@pytest.fixture
def ccstudiodss_session(pytestconfig):
    ccxml = pytestconfig.getoption('ccxml')

    with ccstudiodss.api.Session(ccxml=ccxml) as session:
        yield session


def pytest_addoption(parser):
    group = parser.getgroup('ccstudiodss')

    group.addoption('--ccs-base-path')
    group.addoption('--ccxml')


def pytest_configure(config):
    base_path = config.getoption('ccs_base_path')

    if base_path is None:
        base_path = ccstudiodss.utils.find_base_path()

    ccstudiodss.api.add_jars(base_path=base_path)
