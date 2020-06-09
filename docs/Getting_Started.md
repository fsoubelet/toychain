# Getting Started

## Installation

There are two possible methods for installing and running toychain: either as a Python package with [pip], or as a [Docker] image.

### With pip

You can now install this simply in a virtual environment with `pip install toychain`.

!!! tip "Installation in a virtual environment"
    Don't know what a **virtual environment** is or how to set it up? Here is a good
    [primer on virtual environments][virtual_env_primer] by RealPython.

??? note "How about a development environment?"

    Sure thing. This repository uses [Poetry] as a build tool. To set yourself up,
    get a local copy through VCS and run `poetry install`. You're now good to go, code away!
    
    The `poetry run node` command is predefined to start up a node, by default at
    `localhost:5000`. Additionally, you can specify the host and port on which to
    run the node with the `--host` and `--port` flags. You can then use the same
    command to spin up several nodes on different ports.

### With Docker

It is possible to run nodes as Docker containers.
For now, there is no existing image you can pull from Docker Hub, so you will have to build it localy.
To do so, clone the repository and build the image with `docker build -t blockchain .`

## Running

### As a Python Package

The usage is simple and goes as `python -m toychain`.

??? summary "Command Line Options"
    
    You can specify the port as well as the host on which to run the node
    with the `--port` and `--host` flags. The usage goes as:

    ``` bash
    usage: __main__.py [-h] [-p PORT] [--host HOST]
    
    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  The port on which to run a node. Defaults to 5000.
      --host HOST           The host on which to run the node. Defaults to
                            '127.0.0.1', known as 'localhost'.
    ```

### As a Docker Container

Assuming you have built the image as instructed above, you can then run a container by mapping the node's port to a desired one at `localhost` on your machine.
To map the node to port 5000, run:
```bash
docker run --init --rm -p 5000:5000 blockchain
```

To emulate additional nodes, vary the public port number:
```bash
docker run --init --rm -p 5001:5000 blockchain
docker run --init --rm -p 5002:5000 blockchain
docker run --init --rm -p 5003:5000 blockchain
```

You can then play around by **POST**ing to `/nodes/register` to add all your running instances to one another's networks, **POST**ing transactions, mining new blocks, and resolving the blockchain.

Refer to the `Functionality` section of this documentation for more information.

[Docker]: https://www.docker.com/
[pip]: https://pip.pypa.io/en/stable/
[Poetry]: https://python-poetry.org/
[virtual_env_primer]: https://realpython.com/python-virtual-environments-a-primer/