import setuptools


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="capes-btd-fetcher",
    author="Daniel K. Komesu",
    author_email="daniel@dkko.me",
    description="Data fetcher of CAPES' Catálogo de Teses e Dissertações",
    long_description=long_description,
    install_requires=["requests"],
    packages=["capes_btd_fetcher"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
