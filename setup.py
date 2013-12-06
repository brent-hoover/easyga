from setuptools import setup
import easyga

setup(
    name="easyga",
    version='.'.join([str(v) for v in easyga.__version__]),
    zip_safe=False,
    platforms='any',
    packages=['easyga'],
    scripts=['easyga/bin/run_gaserver.py'],
    url="https://github.com/dantezhu/easyga",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="make it easier to use pyga with zmq. and make pyga compatible with flask and django.",
    )
