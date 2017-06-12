#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'glob2',
    'arrow'
]

setup(
    name='testcube-client',
    version='0.1.4',
    description="A Python client for testcube. (https://github.com/tobyqin/testcube)",
    long_description=readme + '\n\n' + history,
    author="Toby Qin",
    author_email='toby.qin@live.com',
    url='https://github.com/tobyqin/testcube-client',
    packages=[
        'testcube_client',
    ],
    package_dir={'testcube_client':
                     'testcube_client'},
    entry_points={
        'console_scripts': [
            'testcube-client=testcube_client.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='testcube, testcube-client, test platform, test client',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests.default'
)
