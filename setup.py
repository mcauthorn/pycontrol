from setuptools import setup

setup(
    name='pycontrol',
    description='Library for F5 iControl API',
    long_description="""pyControl is a Python-based library that integrates
                        with F5's BIG-IP iControl management API.""",
    version='2.1',
    license='GPL',
    author='Matt Cauthorn',
    author_email='mcauthorn@gmail.com',
    url='https://github.com/mcauthorn/pycontrol',
    keywords='iControl F5 API',
    #py_modules=['pycontrol'],
    packages=['pycontrol',],
    install_requires=['distribute', 'suds>=0.3.9'],
    platforms='any',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
