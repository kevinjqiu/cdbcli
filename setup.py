import setuptools

setuptools.setup(
    name="cdbcli",
    version="0.1.1",
    url="https://github.com/kevinjqiu/cdbcli",

    author="Kevin J. Qiu",
    author_email="kevin@idempotent.ca",

    description="Interactive command line shell for CouchDB",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'cdbcli=cdbcli:main'
        ]
    },
)
