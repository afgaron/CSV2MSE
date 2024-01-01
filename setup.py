import versioneer
from setuptools import setup

setup(
    name="csv2mse",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Generic CSV to MSE importer",
)