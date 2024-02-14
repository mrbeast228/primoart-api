from starlette.responses import JSONResponse

from orm.config import config
if config.db_type == 'clickhouse':
    import orm.clickhouse as ORM
elif config.db_type == 'postgres':
    import orm.postgres as ORM
else:
    raise TypeError(f'Database {config.db_type} not supported!')
from api.core import APICore, app


class GET(APICore):
    def __init__(self):
        super().__init__()
        @app.get("/transactions")
        async def get_transactions():
            try:
                transactions = ORM.Transaction.select()
                subresult = [ORM.BaseModel.extract_data_from_select_dict(transaction.__dict__)
                             for transaction in transactions]
                return JSONResponse(content={'transactions': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transactions: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}")
        async def get_transaction_by_id(transaction_id: str):
            try:
                self.validate_uuid4(transaction_id)

                transactions = ORM.Transaction.select()\
                    .where(ORM.Transaction.transactionid == transaction_id)
                if not transactions:
                    return JSONResponse(content={'error': 'Transaction not found!'}, status_code=404)

                result_transaction = ORM.BaseModel.extract_data_from_select_dict(transactions[0].__dict__)
                return JSONResponse(content={'transactions': [self.json_reserialize(result_transaction)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transaction: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps")
        async def get_transaction_steps(transaction_id: str):
            try:
                self.validate_uuid4(transaction_id)

                transaction_steps = ORM.Step_Info.select().where(
                    ORM.Step_Info.transactionid == transaction_id)
                if not transaction_steps:
                    return JSONResponse(content={'error': 'Transaction steps not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(step.__dict__)
                             for step in transaction_steps]
                return JSONResponse(content={'steps': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transaction steps: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/{step_id}")
        @app.get("/steps/{step_id}")
        async def get_transaction_step_by_id(step_id: str, transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(step_id)

                step = ORM.Step_Info.select().where(ORM.Step_Info.stepid == step_id)[0]
                if not step:
                    return JSONResponse(content={'error': 'Step not found!'}, status_code=404)

                result_step = ORM.BaseModel.extract_data_from_select_dict(step.__dict__)
                return JSONResponse(content={'steps': [self.json_reserialize(result_step)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting step: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/{step_id}/runs")
        @app.get("/steps/{step_id}/runs")
        async def get_step_runs(step_id: str, transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(step_id)

                step_runs = ORM.Step_Run.select().where(ORM.Step_Run.stepid == step_id)
                if not step_runs:
                    return JSONResponse(content={'error': 'Step runs not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(run.__dict__)
                             for run in step_runs]
                return JSONResponse(content={'step_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting step runs: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/{step_id}/runs/{run_id}")
        @app.get("/steps/{step_id}/runs/{run_id}")
        async def get_step_run_by_id(run_id: str, step_id: str, transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(step_id)
                self.validate_uuid4(run_id)

                run = ORM.Step_Run.select().where(ORM.Step_Run.steprunid == run_id)[0]
                if not run:
                    return JSONResponse(content={'error': 'Run not found!'}, status_code=404)

                result_run = ORM.BaseModel.extract_data_from_select_dict(run.__dict__)
                return JSONResponse(content={'step_runs': [self.json_reserialize(result_run)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting run: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/runs")
        async def get_transaction_runs(transaction_id: str):
            try:
                self.validate_uuid4(transaction_id)

                transaction_runs = ORM.Transaction_Run.select().where(
                    ORM.Transaction_Run.transactionid == transaction_id)
                if not transaction_runs:
                    return JSONResponse(content={'error': 'Transaction runs not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(run.__dict__)
                             for run in transaction_runs]
                return JSONResponse(content={'runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transaction runs: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/runs/{run_id}")
        @app.get("/runs/{run_id}")
        async def get_transaction_run_by_id(run_id: str, transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(run_id)

                runs = ORM.Transaction_Run.select().where(ORM.Transaction_Run.transactionrunid == run_id)
                if not runs:
                    return JSONResponse(content={'error': 'Run not found!'}, status_code=404)

                result_run = ORM.BaseModel.extract_data_from_select_dict(runs[0].__dict__)
                return JSONResponse(content={'runs': [self.json_reserialize(result_run)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting run: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/runs/{run_id}/steps")
        @app.get("/runs/{run_id}/steps")
        async def get_run_steps(run_id: str, transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(run_id)

                run_steps = ORM.Step_Run.select().where(ORM.Step_Run.transactionrunid == run_id)
                if not run_steps:
                    return JSONResponse(content={'error': 'Run steps not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(step.__dict__)
                             for step in run_steps]
                return JSONResponse(content={'step_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting run steps: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/runs/{run_id}/steps/{step_id}")
        @app.get("/runs/{run_id}/steps/{step_id}")
        async def get_run_step_by_id(step_id: str, run_id: str, transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(step_id)
                self.validate_uuid4(run_id)

                step = ORM.Step_Run.select().where(ORM.Step_Run.steprunid == step_id)[0]
                if not step:
                    return JSONResponse(content={'error': 'Step not found!'}, status_code=404)

                result_step = ORM.BaseModel.extract_data_from_select_dict(step.__dict__)
                return JSONResponse(content={'step_runs': [self.json_reserialize(result_step)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting step: {e}'}, status_code=500)
