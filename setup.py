from distutils.core import setup, Extension
import os
from sys import exit


if 'SAUCE_CONNECT_DIR' in os.environ:
    sc_dir = os.environ['SAUCE_CONNECT_DIR']
else:
    print "Unable to find Sauce Connect directory."
    print "Please set SAUCE_CONNECT_DIR environment variable."
    exit(-1)


runtime_library_dirs = []
if 'OPENSSL_DIR' in os.environ:
    # depends upon openssl 1, which might not be default
    runtime_library_dirs = [os.environ['OPENSSL_DIR']]


libsauceconnect = Extension('libsauceconnect',
    sources              = ['saucelabs/libsauceconnect.c'],
    include_dirs         = ['%s/include' % sc_dir],
    libraries            = ['ssl', 'crypto', 'curl', 'event', 'event_openssl'],
    extra_objects        = [ '%s/lib/libsauceconnect.a' % sc_dir],
    runtime_library_dirs = runtime_library_dirs
)


setup(name       = 'LibSauceConnect',
    version      = '0.1',
    description  = 'Sauce Connect Python Bindings',
    author       = "Isaac Murchie",
    author_email = "isaac@saucelabs.com",
    ext_modules  = [libsauceconnect],
    packages     = ['saucelabs'],
    license      = "Apache 2.0")
