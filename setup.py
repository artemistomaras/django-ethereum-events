import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

extras_require = {
    'tester': [
        'eth-tester[py-evm]==v0.2.0-beta.2'
    ],
    'dev': [
        'tox>=1.8.0'
        'twine>=1.13,<2'
        'wheel'
    ],
    'linter': [
        'flake8==3.7.9'
    ]
}

extras_require['dev'] = (
    extras_require['tester'],
    extras_require['dev'],
    extras_require['linter']
)

setup(
    name='django-ethereum-events',
    version='4.1.0',
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    install_requires=[
        'Django>=1.11',
        'celery>=3.1.25',
        'django-solo>=1.1.0',
        'web3>=5.5.0,<6',
    ],
    extras_require=extras_require,
    python_requires='>=3.6,<4',
    license='MIT License',
    description='Django Ethereum Events',
    long_description=README,
    url='https://github.com/artemistomaras/django-ethereum-events',
    author='Artemios Tomaras',
    author_email='artemistomaras@gmail.com',
    keywords='django ethereum',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
