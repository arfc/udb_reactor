from distutils.core import setup


VERSION = '0.0.1'
setup_kwargs = {
    "version": VERSION,
    "description": 'Data Reactor',
    "author": 'Jin Whan Bae',
    }

if __name__ == '__main__':
    setup(
        name='data_reactor',
        packages=["data_reactor"],
        **setup_kwargs
        )
