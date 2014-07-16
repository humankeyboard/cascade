from setuptools import setup, find_packages

setup(
    name = "cascade",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['progressbar', 'imaplib2'],
    author = "Oz Akan",
    author_email = "code@akan.me",
    description = "Cascade copies e-mails between IMAP servers",
    license = "Apache Version 2.o",
    url = "https://github.com/humankeyboard/cascade",
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
    ],
    entry_points = {
        'console_scripts' : [
            'cascade = cmd.app:app'
        ]
    }
    
)
