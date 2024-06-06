from setuptools import setup, find_packages

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name='bit-chess-python',
    version=version,
    author='Andrew Yin',
    author_email='andrewyingo@gmail.com',
    description='Bitboard Chess implementation written entirely in Python',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
