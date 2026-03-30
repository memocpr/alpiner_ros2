import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_descritpion = fh.read()

setuptools.setup(
    name='pmi',
    version='1.0.0',
    author='Syrto AG',
    author_email='gilles.mottiez@syrto.ch',
    description='AT-COM python machine interface',
    long_description=long_descritpion,
    packages=setuptools.find_packages(),
    package_dir={'':'src'}
)
