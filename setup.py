import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt', encoding="utf-8") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='labfra_bot',
    version='0.0.1',
    author='Pablo Gomez',
    author_email='pablosgomez50@gmail.com',
    description='Paquete con la funcionalidad del robot de discord',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/PabloSGomez50/bot_labFra',
    project_urls = {
        "Bug Tracker": "https://github.com/PabloSGomez50/bot_labFra/issues"
    },
    license='MIT',
    packages=['labfra_bot'],
    install_requires=requirements,
    # install_requires=['requests'],
)