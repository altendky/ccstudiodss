import setuptools

import versioneer


with open('README.rst') as f:
    readme = f.read()

setuptools.setup(
    name='ccstudiodss',
    description="Build and load Code Composer Studio projects from the command line.",
    long_description=readme,
    long_description_content_type='text/x-rst',
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
