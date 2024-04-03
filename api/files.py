import uuid
import filetype
from pathlib import Path

from fastapi import UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from api.core import APICore, app
from orm.config import config

class Files(APICore):
    def __init__(self):
        super().__init__()

        self.logs_dir = Path(__file__).parent / '..' / config.logs_dir
        self.screenshots_dir = Path(__file__).parent / '..' / config.screenshots_dir

        @app.get("/logs/{log_id}", tags=['Receive files'])
        async def get_log(log_id: str):
            try:
                self.validate_uuid4(log_id)

                log_path = self.logs_dir / f'{log_id}.log'
                if not log_path.exists():
                    return JSONResponse(content={'error': f'Log {log_id} not found!'}, status_code=404)

                return FileResponse(log_path.resolve())

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting log {log_id}: {e}'}, status_code=500)

        # get log file from POST
        @app.post("/logs", tags=['Upload files'])
        async def create_log(file: bytes = File(...)):
            try:
                log_id = str(uuid.uuid4())
                log_path = (self.logs_dir / f'{log_id}.log').resolve()

                with open(log_path, 'wb') as buffer:
                    buffer.write(file)
                return JSONResponse(content={'message': f'Log created successfully!', 'log_id': log_id})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating log: {e}'}, status_code=500)

        @app.get("/screenshots/{screenshot_id}", tags=['Receive files'])
        async def get_screenshot(screenshot_id: str):
            try:
                self.validate_uuid4(screenshot_id)

                screenshot_path = self.screenshots_dir / screenshot_id
                if not screenshot_path.exists():
                    return JSONResponse(content={'error': f'Screenshot {screenshot_id} not found!'}, status_code=404)

                return FileResponse(screenshot_path.resolve(), media_type=filetype.guess(screenshot_path).mime)

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting screenshot {screenshot_id}: {e}'}, status_code=500)

        # get screenshot file from POST
        @app.post("/screenshots", tags=['Upload files'])
        async def create_screenshot(file: UploadFile = File(...)):
            try:
                screenshot_id = str(uuid.uuid4())
                screenshot_path = (self.screenshots_dir / screenshot_id).resolve()

                with open(screenshot_path, 'wb') as buffer:
                    buffer.write(await file.read())
                return JSONResponse(content={'message': f'Screenshot created successfully!', 'screenshot_id': screenshot_id})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating screenshot: {e}'}, status_code=500)
