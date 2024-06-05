from setuptools import setup, find_packages
import pypandoc

output = pypandoc.convert_file('README.md', 'rst')
with open('README.rst', 'w') as f:
    f.write(output)

setup(
    name='bit-chess-python',
    version='0.1.0',
    author='Andrew Yin',
    author_email='andrewyingo@gmail.com',
    description='Bitboard Chess implementation written entirely in Python',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
)
