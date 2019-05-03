
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twn_generator-dasteve",
    version="0.0.1",
    author="Stephen Tridgell",
    author_email="stephen.tridgell@sydney.edu.au",
    description="A package to generate verilog for TNNs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/da-steve101/twn_generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
)
