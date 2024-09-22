from setuptools import setup, find_packages

setup(
    name='embodied-agent-eval',
    version='0.0.1',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "lark",
        "bddl-eval",
        "pyquaternion",
        "pddlgym",
        "ipdb",
        "networkx>=3.1",
        "numpy>=1.20.0",
    ],
    include_package_data=True,
    package_data={
        '': ['*.json', '*.xml', '*.md', '*.yaml', "*.txt", "*.pddl"],
    },
    entry_points={
        'console_scripts': [
            'eagent-eval=cli:main',  
        ],
    },
)
