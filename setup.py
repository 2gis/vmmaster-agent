from setuptools import setup,  find_packages

setup(
    name='vmmaster-agent',
    version='0.1',
    description='vmmaster agent for make some utility (take screenshot etc.) on virtual machine',
    url='https://github.com/nwlunatic/vmmaster-agent',
    packages=find_packages(),
    install_requires=[
        "twisted==13.2.0",
        "pyscreenshot==0.3.2"
    ],
    entry_points={
        'console_scripts': [
            'vmmaster_agent = vmmaster_agent.agent:main',
        ],
    },
)