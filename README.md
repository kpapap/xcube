[![Build Status](https://ci.appveyor.com/api/projects/status/h4m43pwga7pjoftl/branch/main?svg=true)](https://ci.appveyor.com/project/bcdev/xcube)
[![codecov](https://codecov.io/gh/dcs4cop/xcube/branch/main/graph/badge.svg)](https://codecov.io/gh/dcs4cop/xcube)
[![Documentation Status](https://readthedocs.org/projects/xcube/badge/?version=latest)](https://xcube.readthedocs.io/en/latest/?badge=latest)
[![PyPI Version](https://img.shields.io/pypi/v/xcube-core)](https://pypi.org/project/xcube-core/)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/xcube/badges/version.svg)](https://anaconda.org/conda-forge/xcube)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/xcube/badges/license.svg)](https://anaconda.org/conda-forge/xcube)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

xcube is a Python toolkit for managing geospatial data cubes.

It is based on popular data science packages such as
[xarray](http://xarray.pydata.org/), [Zarr](https://zarr.readthedocs.io/), and [Dask](https://dask.org/).

Find out more in the [xcube Documentation](https://xcube.readthedocs.io).

# Create and run docker image

Build the server image by running:

```
sudo docker build -t xcube:0.10.0 .
```

This creates an image of the server, with a configuration read from "/home/xcube/examples/serve/demo/config.yml" inside the image. To access the server on your host machine, port 8080 (localhost:8080), run:

```
docker run -d -p 8080:8080 xcube:0.10.0
```

**Or, if you want to send other parameters to the server**

Build the server image by running:

```
sudo docker build -t xcube:0.10.0 .
```

This creates an image of the server, with a configuration read from "/home/xcube/examples/serve/demo/config.yml" inside the image. To set the server on a different port, e.g. 8081 and access the server on your host machine, port 8081 (localhost:8081), run:

```
docker run -d -p 8081:8081 xcube:0.10.0 /bin/bash -c "xcube serve -v --address 0.0.0.0 --port 8081 -c /home/xcube/examples/serve/demo/config.yml"
```

# Access viewer

Go to e.g.

```
http://localhost:8080/viewer
```

# Access Web JSON

Go to e.g.

```
http://localhost:8080
```

# Access Web API

Go to e.g.

```
http://localhost:8080/openapi.html
```
