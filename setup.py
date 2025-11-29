# /home/max/code/simpleKnowledgeBaseAI/setup.py
from setuptools import setup, find_packages

setup(
    name='simpleKnowledgeBaseAI',
    version='0.1.0',
    packages=find_packages(), 
    entry_points={
        'console_scripts': [
            # Syntax: command_name = package.module:function
            'kb=cli.commandline:main',
        ],
    },
)