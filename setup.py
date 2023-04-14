from setuptools import setup, find_packages

setup(
    name='key-point-finder',
    version='0.0.1',
    author='Samuel W. Failor',
    author_email='samuel.failor@gmail.com',
    url='http://github.com/sfailor/key-point-finder',
    install_requires=   [
                            'pyqtgraph',
                            'PyQt5',
                            'numpy',                       
                        ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)