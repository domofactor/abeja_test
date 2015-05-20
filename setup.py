try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Abeja Test',
    'author': 'Terrell Broomer',
    'url': 'http://github.com/domofactor.com/abeja_test',
    'author_email': 'sftmb4@gmail.com',
    'version': '0.1',
    'install_requires': ['beautifulsoup4','boto'],
    'packages': ['abeja_test'],
    'scripts': [],
    'name': 'abeja_test'
}

setup(**config)
