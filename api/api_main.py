import uvicorn
from starlette.middleware.cors import CORSMiddleware

from api.core import app, APICore
from api.add import POST
from api.edit import PUT
from api.sdr import SingleGET
from api.read import MultiGET
from api.heatmap import MatrixGET
from api.remove import DELETE
from api.files import Files

from orm.config import config


class API(APICore):
    def __init__(self):
        super().__init__()
        self.allowed_origins = config.cors_origins.split(',')

        self.prepare_middlewares()
        self.implement_methods()

    def prepare_middlewares(self):
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        # auth middleware to be implemented

    def implement_methods(self):
        # constructors of classes adding decorated functions for FastAPI
        MatrixGET() # must be before single get!
        SingleGET()
        MultiGET()
        POST()
        PUT()
        DELETE()
        Files()

    def run(self):
        uvicorn.run(app, host=config.api_endpoint, port=config.api_port)

if __name__ == '__main__':
    API().run()
