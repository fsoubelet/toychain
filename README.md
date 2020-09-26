<h1 align="center">
  <b>toychain</b>
</h1>

toychain is a very simplistic blockchain node modeling in Python.
While the code is my own adaptation, the implementation and architecture is from the very good [tutorial] by Daniel van Flymen.
This adaptation uses [FastAPI] as a web framework, and [uvicorn] as ASGI server instead of the `Flask` app from van Flymen's tutorial.

Link to [documentation].

## License

Copyright &copy; 2020 Felix Soubelet. [MIT License](LICENSE)

[documentation]: https://fsoubelet.github.io/toychain/
[FastAPI]: https://fastapi.tiangolo.com/
[tutorial]: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
[uvicorn]: https://www.uvicorn.org/