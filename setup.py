import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    "Django>=1.10",
    "celery>=3.1.25,<4.0.0rc3",
    "ethereum>=1.6.0,<2.0.0",
    "ethereum-abi-utils>=0.4.1",
    "ethereum-utils>=0.4.0",
    "django-solo>=1.1.0",
    "web3[tester]"
]

setup(
    name='django-ethereum-events',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
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
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
