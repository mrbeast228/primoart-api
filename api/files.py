import filetype
from pathlib import Path

from fastapi import UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from api.core import APICore, app
from orm.config import config
import orm.postgres as ORM

class Files(APICore):
    def __init__(self):
        super().__init__()

        self.logs_dir = Path(__file__).parent / '..' / config.logs_dir
        self.screenshots_dir = Path(__file__).parent / '..' / config.screenshots_dir

        @app.get("/logs/{transaction_run_id}", tags=['Receive files'])
        async def get_log(transaction_run_id: str):
            try:
                self.validate_uuid4(transaction_run_id)

                log_base64 = ORM.Transaction_Run.select(ORM.Transaction_Run.log)\
                    .where(ORM.Transaction_Run.transactionrunid == transaction_run_id).scalar()
                if not log_base64:
                    return JSONResponse(content={'error': f'Log of transaction run {transaction_run_id} not found!'}, status_code=404)
                return JSONResponse(content={'base64': log_base64}) # TODO: implement auto-decoding and uploading a real file

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting log {transaction_run_id}: {e}'}, status_code=500)

        @app.get("/screenshots/{transaction_run_id}", tags=['Receive files'])
        async def get_screenshot(transaction_run_id: str):
            try:
                self.validate_uuid4(transaction_run_id)

                screenshot_base64 = ORM.Transaction_Run.select(ORM.Transaction_Run.screenshot)\
                    .where(ORM.Transaction_Run.transactionrunid == transaction_run_id).scalar()
                if not screenshot_base64:
                    return JSONResponse(content={'error': f'Screenshot of transaction run {transaction_run_id} not found!'}, status_code=404)
                return JSONResponse(content={'base64': screenshot_base64}) # TODO: implement auto-decoding and uploading a real file
                #return FileResponse(screenshot_path.resolve(), media_type=filetype.guess(screenshot_path).mime)

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting screenshot {transaction_run_id}: {e}'}, status_code=500)
