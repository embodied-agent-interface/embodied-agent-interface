from setuptools import setup, find_packages

setup(
    name='eai-eval',
    version='1.0.5',
    author='stanford',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/embodied-agent-interface/embodied-agent-interface",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        "lark",
        "bddl-eval",
        "pyquaternion",
        "pddlgym",
        "ipdb",
        "networkx>=3.1",
        "numpy>=1.20.0",
        "fire",
        "gdown",
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'eai-eval=eai_eval.cli:main',  
        ],
    },
)
