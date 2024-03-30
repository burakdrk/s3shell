from setuptools import setup, find_packages

setup(
    name='s3shell',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            's3shell = s3shell:main',
        ],
    },
)
