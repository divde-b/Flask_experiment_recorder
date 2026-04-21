from setuptools import setup, Extension
import pybind11

ext_module = Extension(
    'sim_metrics',
    sources=['levenshtein.cpp'],
    include_dirs=[pybind11.get_include()],
    language='c++',
    extra_compile_args=['-std=c++11', '-O3']
)

setup(
    name='sim_metrics',
    version='0.1',
    description='C++ extension for string similarity',
    ext_modules=[ext_module]
)