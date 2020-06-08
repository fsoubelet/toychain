<h1 align="center">
  <b>toychain</b>
</h1>

toychain is a very simplistic blockchain node modeling in Python.
While the code is my own adaptation, the implementation is from the very good [tutorial][tutorial] by Daniel van Flymen.
This adaptation uses [FastAPI][fastapi] as a web framework, and [uvicorn][uvicorn] as ASGI server instead of the `Flask` app from van Flymen's tutorial.

[fastapi]: https://fastapi.tiangolo.com/
[tutorial]: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
[uvicorn]: https://www.uvicorn.org/