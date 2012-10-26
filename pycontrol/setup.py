
from setuptools import setup

setup(
    name='pycontrol',
    description='Library for F5 iControl API',
    long_description="""pyControl is a Python-based library that integrates
                        with F5's BIG-IP iControl management API.""",
    version='2.0.1r86',
    license='GPL',
    url='https://devcentral.f5.com/Default.aspx?tabid=149',
    keywords='iControl F5 API',
    py_modules=['pycontrol'],
    install_requires=['distribute', 'suds>=0.3.9'],
    platforms='any',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
