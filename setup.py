import setuptools

setuptools.setup(
    name='ccstudiodss',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'dss = ccstudiodss.cli:cli',
        ],
        'pytest11': [
            'ccstudiodss = ccstudiodss.pytest [test]',
        ]
    },
    install_requires=[
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
