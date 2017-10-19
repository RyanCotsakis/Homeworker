from distutils.core import setup
import py2exe

setup(
    console=['homeworker.py'],
    options={ 
                'py2exe': 
                { 
                    'includes': []
                }
            },
    )