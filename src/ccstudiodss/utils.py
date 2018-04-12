import os
import pathlib
import sys


class BasePathError(Exception):
    pass


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
