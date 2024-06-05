from setuptools import setup, find_packages
setup(
    name='bit-chess',
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
)