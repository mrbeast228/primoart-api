import datetime
from fastapi import Query
from starlette.responses import JSONResponse

from orm.config import config
if config.db_type == 'clickhouse':
    import orm.clickhouse as ORM
elif config.db_type == 'postgres':
    import orm.postgres as ORM
else:
    raise TypeError(f'Database {config.db_type} not supported!')

from api.core import APICore, app


class Filters(APICore):
    def __init__(self):
        super().__init__()
        @app.get("/transactions/filter")
        async def get_filtered_transactions(key: str = Query(..., example="name"),
                                            value: str = Query(..., example="tr-robot-ubuntu"),
                                            type: str | None = Query(default=None, example="eq")):
            try:
                if not value:
                    return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                if not type:
                    type = 'eq'

                # get filtering based on type (compatible with bash-like comparison operators)
                transactions = ORM.Transaction.select() \
                    .where(self.bash_comparsion(type, getattr(ORM.Transaction, key), value))

                if not transactions:
                    return JSONResponse(content={'error': 'No transactions found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(transaction.__dict__)
                             for transaction in transactions]
                return JSONResponse(content={'transactions': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering transactions: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/filter")
        @app.get("/steps/filter")
        async def get_filtered_transaction_steps(key: str = Query(..., example="name"),
                                                 value: str = Query(..., example="step-1"),
                                                 type: str | None = Query(default=None, example="eq"),
                                                 transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                if not value:
                    return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                if not type:
                    type = 'eq'

                # get filtering based on type (compatible with bash-like comparison operators)
                # WARNING: here make possible to filter without transactionid if it's empty
                if transaction_id:
                    transaction_steps = ORM.Step_Info.select() \
                        .where(self.bash_comparsion(type, getattr(ORM.Step_Info, key), value),
                               ORM.Step_Info.transactionid == transaction_id)
                else:
                    transaction_steps = ORM.Step_Info.select() \
                        .where(self.bash_comparsion(type, getattr(ORM.Step_Info, key), value))

                if not transaction_steps:
                    return JSONResponse(content={'error': 'No transaction steps found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(step.__dict__)
                             for step in transaction_steps]
                return JSONResponse(content={'steps': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering transaction steps: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/runs/filter")
        async def get_filtered_transaction_runs(transaction_id: str,
                                                key: str = Query(..., example="date"),
                                                start: datetime.datetime | None = Query(None, example="2024-02-14"),
                                                end: datetime.datetime | None = Query(None, example="2030-01-01"),
                                                value: str | None = Query(None, description="used only for filtering by name as for transactions"),
                                                type: str | None = None):
            try:
                self.validate_uuid4(transaction_id)
                if key == 'date':
                    if not start or not end:
                        return JSONResponse(content={'error': 'Start and end dates are required!'}, status_code=400)
                    transactions_runs = ORM.Transaction_Run.select()\
                                       .where(ORM.Transaction_Run.transactionid == transaction_id,
                                              ORM.Transaction_Run.runstart >= start,
                                              ORM.Transaction_Run.runstart <= end)

                else:
                    if not value:
                        return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                    if not type: # set to equal by default
                        type = 'eq'

                    # get filtering based on type (compatible with bash-like comparison operators)
                    transactions_runs = ORM.Transaction_Run.select() \
                        .where(self.bash_comparsion(type, getattr(ORM.Transaction_Run, key), value),
                               ORM.Transaction_Run.transactionid == transaction_id)

                if not transactions_runs:
                    return JSONResponse(content={'error': 'No transactions found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(transaction_run.__dict__)
                            for transaction_run in transactions_runs]
                return JSONResponse(content={'transactions_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering transactions: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/{step_id}/runs/filter")
        @app.get("/steps/{step_id}/runs/filter")
        async def get_filtered_step_runs(step_id: str,
                                         key: str = Query(..., example="date"),
                                         start: datetime.datetime | None = Query(None, example="2024-02-14"),
                                         end: datetime.datetime | None = Query(None, example="2030-01-01"),
                                         value: str | None = Query(None, description="used only for filtering by name as for steps"),
                                         type: str | None = None,
                                         transaction_id: str = ''):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(step_id)

                if key == 'date':
                    if not start or not end:
                        return JSONResponse(content={'error': 'Start and end dates are required!'}, status_code=400)
                    step_runs = ORM.Step_Run.select()\
                                       .where(ORM.Step_Run.stepid == step_id,
                                              ORM.Step_Run.runstart >= start,
                                              ORM.Step_Run.runstart <= end)

                else:
                    if not value:
                        return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                    if not type: # set to equal by default
                        type = 'eq'

                    # get filtering based on type (compatible with bash-like comparison operators)
                    step_runs = ORM.Step_Run.select() \
                        .where(self.bash_comparsion(type, getattr(ORM.Step_Run, key), value),
                               ORM.Step_Run.stepid == step_id)

                if not step_runs:
                    return JSONResponse(content={'error': 'No step runs found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(step_run.__dict__)
                            for step_run in step_runs]
                return JSONResponse(content={'step_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering step runs: {e}'}, status_code=500)
