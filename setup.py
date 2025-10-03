from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hse-ml-contrast-checker",
    version="0.1.0",
    author="Zebzeev Daniil",
    description="A Python tool for analyzing text and background contrast using ML approaches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DaniilZebzeev/hse-ml-contrast-checker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "contrast-checker=contrast_checker.cli:main",
        ],
    },
)
