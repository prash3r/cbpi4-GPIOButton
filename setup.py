from setuptools import setup

setup(name='cbpi4_GPIOButton',
      version='0.0.1',
      description='CraftBeerPi Plugin to make api calls with Buttons wired to GPIO pins',
      author='Tim Hanke',
      author_email='pipy@prash3r.de',
      url='https://github.com/prash3r/cbpi4-GPIOButton',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_GPIOButton': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_GPIOButton'],
     )