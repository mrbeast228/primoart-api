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

        @app.get("/robots/filter")
        async def get_filtered_robots(key: str = Query(..., example="name"),
                                      value: str = Query(..., example="robot-1"),
                                      type: str | None = Query(default=None, example="eq"),
                                      first: int = Query(default=-1, example=5)):
            try:
                if not value:
                    return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                if not type:
                    type = 'eq'

                # get filtering based on type (compatible with bash-like comparison operators)
                robots = ORM.Robots.select() \
                    .where(self.bash_comparsion(type, getattr(ORM.Robots, key), value))

                if not robots:
                    return JSONResponse(content={'error': 'No robots found!'}, status_code=404)

                subresult = self.get_first_n(robots, first)
                return JSONResponse(content={'robots': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering robots: {e}'}, status_code=500)


        @app.get("/services/filter")
        async def get_filtered_services(key: str = Query(..., example="name"),
                                        value: str = Query(..., example="service-1"),
                                        type: str | None = Query(default=None, example="eq"),
                                        first: int = Query(default=-1, example=5)):
            try:
                if not value:
                    return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                if not type:
                    type = 'eq'

                # get filtering based on type (compatible with bash-like comparison operators)
                services = ORM.Services.select() \
                    .where(self.bash_comparsion(type, getattr(ORM.Services, key), value))

                if not services:
                    return JSONResponse(content={'error': 'No services found!'}, status_code=404)

                subresult = self.get_first_n(services, first)
                return JSONResponse(content={'services': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering services: {e}'}, status_code=500)


        @app.get("/services/{service_id}/processes/filter")
        @app.get("/processes/filter")
        async def get_filtered_processes(key: str = Query(..., example="name"),
                                            value: str = Query(..., example="process-1"),
                                            type: str | None = Query(default=None, example="eq"),
                                            service_id: str = '',
                                            first: int = Query(default=-1, example=5)):
                try:
                    if service_id:
                        self.validate_uuid4(service_id)
                    if not value:
                        return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                    if not type:
                        type = 'eq'

                    # get filtering based on type (compatible with bash-like comparison operators)
                    # WARNING: here make possible to filter without serviceid if it's empty
                    if service_id:
                        processes = ORM.Business_Process.select() \
                            .where(self.bash_comparsion(type, getattr(ORM.Business_Process, key), value),
                                ORM.Business_Process.serviceid == service_id)
                    else:
                        processes = ORM.Business_Process.select() \
                            .where(self.bash_comparsion(type, getattr(ORM.Business_Process, key), value))

                    if not processes:
                        return JSONResponse(content={'error': 'No processes found!'}, status_code=404)

                    subresult = self.get_first_n(processes, first)
                    return JSONResponse(content={'processes': self.json_reserialize(subresult)})

                except Exception as e:
                    return JSONResponse(content={'error': f'Error while filtering processes: {e}'}, status_code=500)


        @app.get("/business_processes/{process_id}/transactions/filter")
        @app.get("/transactions/filter")
        async def get_filtered_transactions(key: str = Query(..., example="name"),
                                            value: str = Query(..., example="tr-robot-ubuntu"),
                                            type: str | None = Query(default=None, example="eq"),
                                            process_id: str = '',
                                            first: int = Query(default=-1, example=5)):
            try:
                if process_id:
                    self.validate_uuid4(process_id)
                if not value:
                    return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                if not type:
                    type = 'eq'

                # get filtering based on type (compatible with bash-like comparison operators)
                # WARNING: here make possible to filter without processid if it's empty
                if process_id:
                    transactions = ORM.Transaction.select() \
                        .where(self.bash_comparsion(type, getattr(ORM.Transaction, key), value),
                            ORM.Transaction.processid == process_id)
                else:
                    transactions = ORM.Transaction.select() \
                        .where(self.bash_comparsion(type, getattr(ORM.Transaction, key), value))

                if not transactions:
                    return JSONResponse(content={'error': 'No transactions found!'}, status_code=404)

                subresult = self.get_first_n(transactions, first)
                return JSONResponse(content={'transactions': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering transactions: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/filter")
        @app.get("/steps/filter")
        async def get_filtered_transaction_steps(key: str = Query(..., example="name"),
                                                 value: str = Query(..., example="step-1"),
                                                 type: str | None = Query(default=None, example="eq"),
                                                 transaction_id: str = '',
                                                 first: int = Query(default=-1, example=5)):
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

                subresult = self.get_first_n(transaction_steps, first)
                return JSONResponse(content={'steps': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering transaction steps: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/runs/filter")
        @app.get("/runs/filter")
        async def get_filtered_transaction_runs(transaction_id: str = '',
                                                key: str = Query(..., example="date"),
                                                start: datetime.datetime | None = Query(None, example="2024-02-14"),
                                                end: datetime.datetime | None = Query(None, example="2030-01-01"),
                                                value: str | None = Query(None, description="used only for filtering by name as for transactions"),
                                                type: str | None = None,
                                                first: int = Query(default=-1, example=5)):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                if key == 'date':
                    if not start or not end:
                        return JSONResponse(content={'error': 'Start and end dates are required!'}, status_code=400)
                    if transaction_id:
                        transactions_runs = ORM.Transaction_Run.select()\
                                           .where(ORM.Transaction_Run.transactionid == transaction_id,
                                                  ORM.Transaction_Run.runstart >= start,
                                                  ORM.Transaction_Run.runstart <= end)
                    else:
                        transactions_runs = ORM.Transaction_Run.select()\
                                           .where(ORM.Transaction_Run.runstart >= start,
                                                  ORM.Transaction_Run.runstart <= end)

                else:
                    if not value:
                        return JSONResponse(content={'error': 'Filtering value is required!'}, status_code=400)
                    if not type: # set to equal by default
                        type = 'eq'

                    # get filtering based on type (compatible with bash-like comparison operators)
                    if transaction_id:
                        transactions_runs = ORM.Transaction_Run.select() \
                            .where(self.bash_comparsion(type, getattr(ORM.Transaction_Run, key), value),
                                   ORM.Transaction_Run.transactionid == transaction_id)
                    else:
                        transactions_runs = ORM.Transaction_Run.select() \
                            .where(self.bash_comparsion(type, getattr(ORM.Transaction_Run, key), value))

                if not transactions_runs:
                    return JSONResponse(content={'error': 'No transactions runs found!'}, status_code=404)

                subresult = self.get_first_n(transactions_runs, first)
                return JSONResponse(content={'transactions_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering transactions runs: {e}'}, status_code=500)


        @app.get("/transactions/{transaction_id}/steps/{step_id}/runs/filter")
        @app.get("/steps/{step_id}/runs/filter")
        async def get_filtered_step_runs(step_id: str,
                                         key: str = Query(..., example="date"),
                                         start: datetime.datetime | None = Query(None, example="2024-02-14"),
                                         end: datetime.datetime | None = Query(None, example="2030-01-01"),
                                         value: str | None = Query(None, description="used only for filtering by name as for steps"),
                                         type: str | None = None,
                                         transaction_id: str = '',
                                         first: int = Query(default=-1, example=5)):
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

                subresult = self.get_first_n(step_runs, first)
                return JSONResponse(content={'step_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while filtering step runs: {e}'}, status_code=500)
