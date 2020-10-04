import setuptools

with open('README.md','r') as file:
    long_description = file.read()

setuptools.setup(
    name="pycript-Micalobia",
    version="0.0.1",
    author="Micalobia",
    author_email="micalobiabusiness@gmail.com",
    description="A Minecraft datapack support library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https:/github.com/Micalobia/pycript",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6"
)