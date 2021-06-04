from setuptools import find_packages, setup


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="envfrom",
    description="Call child process with custom environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.2.0",
    author="rm_ass",
    author_email="contact@romanmasse.com",
    packages=find_packages(),
    url='http://github.com/rambobinator/envfrom',
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    entry_points={
        "console_scripts": [
            "envfrom = envfrom.envfrom:run"
        ]
    },
    install_requires=[
        "kubernetes>=10.0.1",
        "requests>=2.23.0",
        "nested-lookup>=0.2.21",
        "hvac[parser]>=0.10.5"
    ],
    license="MIT"
)
