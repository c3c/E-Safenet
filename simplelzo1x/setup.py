from distutils.core import setup, Extension
import struct

# It should auto-detect the platform and link against the correct library

module1 = Extension('simplelzo1x',
                    sources = ['simplelzo1xmodule.c'],
                    include_dirs = ['liblzo'],
                    libraries = ['lzo'],
                    library_dirs = ['liblzo/'+str(8 * struct.calcsize("P"))+'bit'])

setup (name = 'simplelzo1x',
       version = '1.1',
       description = '(De)compress with the LZO1X_1 algorithm used in E-Safenet',
       ext_modules = [module1])
