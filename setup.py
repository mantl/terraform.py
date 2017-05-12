# -*- coding: utf-8 -*-
"""Ansible Terraform Inventory."""
# batteries included
from __future__ import absolute_import

from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup


doc_requirements = []
install_requirements = [
    'boto3>=1.4.4,<2',
    'sh>=1.12.13,<2']
release_requirements = [
    'zest.releaser[recommended]>=6.6.5,<6.7']
test_requirements = [
    'coverage>=3,<4',
    'flake8>=3.3.0,<4',
    'hypothesis>=3.7.0,<4',
    'moto>=0.4.31,<1',
    'pydocstyle>=1.1.1,<2',
    'pytest>=2.9.2,<3',
    'pytest-cov>=2.4.0,<3',
    'pytest-flakes>=1.0.1,<2',
    'pytest-mccabe>=0.0.1,<2',
    'moto>=0.4.31,<1']
debug_requirements = [
    'pdbpp>=0.8.3,<1']
dev_requirements = (
    doc_requirements +
    test_requirements +
    release_requirements +
    debug_requirements)
    

entry_points = {
    'console_scripts': ['ati=ati.cli:cli']}

setup(name='ati',
      version='0.4.4.dev0',
      description='Ansible Terraform Inventory',
      author='Brian Hicks',
      author_email='brian@brianthicks.com',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: DevOps',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
      ],
      entry_points=entry_points,
      keywords=['ansible', 'inventory', 'devops', 'terraform'],
      url='https://github.com/sean-abbott/terraform.py',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
      include_package_data=True,
      extras_require={
          'dev': dev_requirements,
          'doc': doc_requirements,
          'release': release_requirements,
          'test': test_requirements},
      install_requires=install_requirements,
      tests_require=test_requirements,
test_suite='tests')
