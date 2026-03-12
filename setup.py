from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="financial_spyder",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "financial-spyder=spyder_app.main:main",
        ],
    },
    author="Financial Spyder Authors",
    description="A robust web crawler and financial analysis tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
