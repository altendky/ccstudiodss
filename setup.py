import setuptools

import versioneer


with open('README.rst') as f:
    readme = f.read()

setuptools.setup(
    name='ccstudiodss',
    description="Build and load Code Composer Studio projects from the command line using the Java DSS library.",
    long_description=readme,
    long_description_content_type='text/x-rst',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    classifiers=[
        # complete classifier list: https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
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
        'lxml',
    ],
    extras_require={
        'java': [
            'jpype1 >= 1.1.2, == 1.*',
        ],
        'dev': [
            'gitignoreio',
        ],
        'test': [
            'pytest',
        ],
    },
)
