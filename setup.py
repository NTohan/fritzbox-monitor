from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("LICENSE", "r") as fh:
    license  = fh.read()

setup(
   name='fritzbox-monitor',
   version='2.0.0',
   description='Fritzbox-Monitor is a real-time service that checks Fritzbox system errors against a set of configured rules.',
   author='Navneet Tohan',
   author_email='navneet.tohan@gmail.com',
   packages=['fritzbox-monitor'],  #same as name
   install_requires=requirements, #external packages as dependencies
   long_description=long_description,      # Long description read from the the readme file
   long_description_content_type="text/markdown",
   license = license,
   scripts=['bin/fritzbox-monitor'],
)
