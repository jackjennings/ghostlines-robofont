from setuptools import setup

setup(
    name='ghostlines-robofont',
    version='0.4.0',
    author='Ghostlines',
    author_email='info@ghostlines.pm',
    py_modules=['ghostlines'],
    url='http://github.com/jackjennings/unicodeset',
    license='LICENSE',
    description='The extension for the platform',
    long_description=open('README.md').read(),
    include_package_data=True,
    package_dir={'': 'src/lib'},
)
