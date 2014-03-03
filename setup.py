# stevedore/example/setup.py
from setuptools import setup, find_packages

setup(
    name='nonobot',
    version='0.1',

    description='The nono bot',

    author='Chmouel Boudjnah',
    author_email='chmouel@chmouel.com',

    url='https://github.com/chmouel/nonobot',
    download_url='https://github.com/chmouel/nonobot/tarball/master',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
    ],

    platforms=['Any'],

    scripts=[],

    provides=['nonobot',
    ],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'nonobot.plugins': [
            'bug = nonobot.plugins.bug:Bug',
        ],
    },

    zip_safe=False,
)
