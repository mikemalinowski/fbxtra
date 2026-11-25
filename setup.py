import os
import setuptools

short_description = 'fbxtra is a utility library to help make interacting with the fbx sdk easier'
if os.path.exists('README.md'):
    with open('README.md', 'r') as fh:
        long_description = fh.read()

else:
    long_description = short_description

setuptools.setup(
    name='fbxtra',
    version='1.3.1',
    author='Mike Malinowski',
    author_email='mike.external@outlook.com',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikemalinowski/fbxtra',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[],
    keywords="fbx fbxsdk",
)
