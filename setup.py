import setuptools
import cdbcli


setuptools.setup(
    name="cdbcli",
    version=cdbcli.__version__,
    url="https://github.com/kevinjqiu/cdbcli",

    author="Kevin J. Qiu",
    author_email="kevin@idempotent.ca",

    description="Interactive command line shell for CouchDB",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        req.strip() for req in open('requirements.txt').readlines() if req
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'cdbcli=cdbcli.main:main'
        ]
    },
)
