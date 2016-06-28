#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup

setup(
    name='isolate',
    packagges=['isolate'],
    version='0.1',
    description='python module to isolated executing programs with namespaces and cgroups',
    author=u'Piotr Wójcik',
    author_mail='piotr_to@op.pl',
    url='https://github.com/meteran/isolate',
    keywords=['isolating', 'isolate', 'namespaces', 'cgroups', 'cgroup', 'namespace'],
    classifiers=[],
    install_requires=[
        'cgroupspy',
    ]
)
