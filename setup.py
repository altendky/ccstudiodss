# setuptools doesn't seem to like unicode 'src' in 2.7/Jython
# from __future__ import unicode_literals

import setuptools

setuptools.setup(
    name='ccstudiodss',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'ccstudiodss = ccstudiodss.cli:cli',
            'ccstudiodssjenv = ccstudiodss.jenv:cli',
        ]
    },
    install_requires=[
        'click',
        'virtualenv',
    ],
    extras_require={
        'dev': [
            'gitignoreio',
        ],
    },
)
