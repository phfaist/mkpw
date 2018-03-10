#!/usr/bin/env python

from setuptools import setup

setup(name='mkpw',
      version='1.0',
      description='Simplistic generation of random passwords',
      author='Philippe Faist',
      author_email='phfa'+str('ist@gm'+'ail')+'.com',
      url='https://github.com/phfaist/mkpw/',
      packages=['mkpw'],
      entry_points={
          'console_scripts': [
              'mkpw = mkpw.__main__:main'
          ]
      },
)
