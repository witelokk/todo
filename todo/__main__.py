import uvicorn

from . import main


if __name__ == "__main__":
    uvicorn.run(main.app)
