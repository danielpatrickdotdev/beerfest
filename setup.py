import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beerfest",
    version="0.0.1a4",
    author="Daniel Patrick",
    author_email="danieljudepatrick@gmail.com",
    description="Django app for beer festival data",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/remarkablerocket/beerfest",
    packages=setuptools.find_packages(),
    install_requires=[
        "django>=2.1",
        "djangorestframework>=3.10",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 2.1",
        "Inteded Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
