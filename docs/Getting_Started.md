# Getting Started

## Installation

There are two possible methods for installing and running toychain: either as a Python package with [pip]{target=_blank}, or as a [Docker]{target=_blank} image.

### With pip

You can now install this simply in a virtual environment with:

```bash
pip install toychain
```

!!! tip "Installation in a virtual environment"
    Don't know what a **virtual environment** is or how to set it up? Here is a good
    [primer on virtual environments][virtual_env_primer]{target=_blank} by RealPython.

??? question "How about a development environment?"

    Sure thing. This repository uses [Poetry]{target=_blank} as a packaging and build tool. To set yourself 
    up, get a local copy through VCS and run:
    
    ```bash
    poetry install
    ```
    You're now good to go, code away!
    To test your changes to the code, you can start up a node at `localhost:5000` with the
    predefined command:
    
    ```bash
    poetry run node
    ```

### With Docker

It is possible to run nodes as Docker containers.
For now, there is no existing image you can pull from Docker Hub, so you will have to build it localy.
To do so, clone the repository and build the image with:

```bash
docker build -t toychain .
```

## Running

### As a Python Package

The usage is simple and goes as:

```bash
python -m toychain
```

??? summary "Command Line Options"
    
    You can specify the port as well as the host on which to run the node
    with the `--port` and `--host` flags, which allows you to easily spin
    up several nodes. The usage goes as:

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
docker run --init --rm -p 5000:5000 toychain
```

To emulate additional nodes, vary the public port number:
```bash
docker run --init --rm -p 5001:5000 toychain
docker run --init --rm -p 5002:5000 toychain
docker run --init --rm -p 5003:5000 toychain
```

You can then play around by POSTing to `/nodes/register` to add all your running instances to one another's networks, POSTing transactions, mining new blocks, and resolving the blockchain.

Refer to the [Functionality](./Functionality/Blockchain.md "Functionality") section of this documentation for more information.

!!! question "What can I do with this?"
    Honestly, not much. This was a learning project and it only models a blockchain's most simple functionality.
    But you can toy around with that, or try to build on it.

[Docker]: https://www.docker.com/
[pip]: https://pip.pypa.io/en/stable/
[Poetry]: https://python-poetry.org/
[virtual_env_primer]: https://realpython.com/python-virtual-environments-a-primer/