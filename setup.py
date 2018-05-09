from distutils.core import setup


VERSION = '0.0.1'
setup_kwargs = {
    "version": VERSION,
    "description": 'UDB Reactor',
    "author": 'Jin Whan Bae',
    }

if __name__ == '__main__':
    setup(
        name='udb_reactor',
        packages=["udb_reactor"],
        **setup_kwargs
        )
