import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QAssembler",
    version="0.1.0",
    author="Erik Jagyugya",
    author_email="jagyugyaerik@gmail.com",
    description="This package creates qsub jobs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jagyugyaerik/qassembler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)


from setuptools import setup


setup(
    setup_requires=['pbr'],
    pbr=True,
)