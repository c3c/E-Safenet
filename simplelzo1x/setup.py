from distutils.core import setup, Extension

module1 = Extension('simplelzo1x',
                    sources = ['simplelzo1xmodule.c'],
                    include_dirs = ['lzo/lzo100'],
                    libraries = ['lzo'],
                    library_dirs = ['lzo/lzo100/x64'])
#                    libraries = ['lzo2'])

setup (name = 'simplelzo1x',
       version = '1.1',
       description = '(De)compress with the LZO1X_1 algorithm used in E-Safenet',
       ext_modules = [module1])
