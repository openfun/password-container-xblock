"""Setup for password_container XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='password_container-xblock',
    version='0.1',
    description=u"This Xblock will restrain acces to its children to a time period and an identication process",
    packages=[
        'password_container',
    ],
    install_requires=[
        'XBlock',
        #'xblockutils'
    ],
    entry_points={
        'xblock.v1': [
            'password_container = password_container:PasswordContainerXBlock',
        ]
    },
    package_data=package_data('password_container', ['static', 'public']),
)
