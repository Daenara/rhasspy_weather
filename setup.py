import setuptools

setuptools.setup(
    name='rhasspy_weather',
    author='Daenara',
    version='0.0.1',
    url='https://github.com/Daenara/rhasspy_weather',
    packages=setuptools.find_packages(),
    py_modules=["rhasspy_weather", "templates", "utils", "api", "data_types", "languages", "output"],
    python_requires='>=3.7',
    install_requires=["requests", "pytz", "paho-mqtt", "suntime", "python-dateutil"],
    package_data={'': ['config.default']}
)
