from setuptools import setup, find_packages

version = '0.0.1.dev0'

setup(
    name = 'txsqlalchemy',
    version = version,
    description = "Just do not ask.",
    classifiers = [
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
        ],
    keywords = "twisted sqlalchemy",
    author = "John Carr",
    author_email = "john.carr@isotoma.com",
    license="Apache Software License",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'Twisted',
        'sqlalchemy',
        ],
    )

