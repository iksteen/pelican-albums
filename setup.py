from setuptools import setup
import os


__version__ = '0.6.0'


requires = [
    'pillow',
]


def read_file(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            return f.read()
    except IOError:
        return ''


setup(
    name='pelican-albums',
    packages=['pelican_albums'],
    version=__version__,
    description='Automatic photo album generation and thumbnailing for Pelican.',
    long_description=read_file('README.rst') + '\n' + read_file('changelog.rst'),
    author='Ingmar Steen',
    author_email='iksteen@gmail.com',
    url='https://github.com/iksteen/pelican-albums/',
    download_url='https://github.com/iksteen/pelican-albums/tarball/v%s' % __version__,
    install_requires=requires,
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
         'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
