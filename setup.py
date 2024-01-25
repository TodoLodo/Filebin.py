from setuptools import setup, find_packages

setup(
    name='your_project',
    version='1.0.0.dev',
    packages=find_packages(),
    install_requires=[],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'your_script = your_project.module1:main',
        ],
    },
)
