import pytest

import ccstudiodss.api

ccxml = None


@pytest.fixture
def ccstudiodss_session():
    import ccstudiodss.api

    with ccstudiodss.api.Session(ccxml=ccxml) as session:
        yield session


def pytest_addoption(parser):
    group = parser.getgroup('ccstudiodss')

    group.addoption('--ccs-base-path')
    group.addoption('--ccxml')


def pytest_configure(config):
    ccstudiodss.api.add_jars(
        base_path=config.getoption('ccs_base_path')
    )

    global ccxml
    ccxml = config.getoption('ccxml')
