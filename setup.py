
# here put the import lib
# python setup.py build_ext

from distutils.core import setup

from Cython.Build import cythonize

setup(ext_modules=cythonize(["app/utils/*.py",
                             "app/*.py",
                             ]),
      )
