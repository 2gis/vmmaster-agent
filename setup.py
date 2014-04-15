from setuptools import setup,  find_packages

setup(
    name='vmmaster-agent',
    version='0.1',
    description='vmmaster agent for make some utility (take screenshot etc.) on virtual machine',
    url='https://github.com/nwlunatic/vmmaster-agent',
    packages=find_packages(),
    install_requires=[
        "twisted==13.2.0",
    ],
    scripts=['bin/vmmaster_agent'],
)