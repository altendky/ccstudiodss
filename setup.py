import setuptools

import versioneer


setuptools.setup(
    name='ccstudiodss',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        'console_scripts': [
            'dss = ccstudiodss.cli:cli',
        ],
        'pytest11': [
            'ccstudiodss = ccstudiodss.pytest [test]',
        ]
    },
    install_requires=[
        'attrs',
        'click',
        'javabridge',
    ],
    extras_require={
        'dev': [
            'gitignoreio',
        ],
        'test': [
            'pytest',
        ],
    },
)
