from setuptools import setup,  find_packages

setup(
    name='vmmaster-agent',
    version='0.2',
    description='vmmaster agent for make some utility (take screenshot etc.) on virtual machine',
    url='https://github.com/2gis/vmmaster-agent',
    packages=find_packages(),
    install_requires=[
        "twisted==14.0.0",
        "autobahn==0.10.3",
        "Pillow==2.5.1"
    ],
    entry_points={
        'console_scripts': [
            'vmmaster_agent = vmmaster_agent.agent:main',
        ],
    },
)
