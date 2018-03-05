from __future__ import unicode_literals

import setuptools

setuptools.setup(
    name='ccstudiodss',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'ccstudiodss = ccstudiodss.cli:cli',
        ]
    },
    install_requires=[
        'click',
    ],
    extras_require={
        'dev': [
            'gitignoreio',
        ],
    },
)
