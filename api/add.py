from fastapi import Body, Query, Path
from starlette.responses import JSONResponse

from orm.config import config

if config.db_type == 'clickhouse':
    import orm.clickhouse as ORM
elif config.db_type == 'postgres':
    import orm.postgres as ORM
else:
    raise TypeError(f'Database {config.db_type} not supported!')

from api.core import APICore, app


class POST(APICore):
    def __init__(self):
        super().__init__()

        @app.post("/transactions")
        async def create_transaction(transaction_data: dict = Body(..., example={"transactions":
                                                                                     [{
                                                                                          "transactionid": "ffffffef-da62-4fed-8d46-c7d6baf80eb3",
                                                                                          "serviceid": "fd2fffef-da62-4fff-8d46-c7d6baf80eb3",
                                                                                          "name": "tr-morning-faithful",
                                                                                          "robotid": "robot-windows",
                                                                                          "description": "An awesome transaction tr-morning-faithful executed by robot robot-windows",
                                                                                          "createddatetime": "2024-02-10 03:12:00.841588+00:00",
                                                                                          "createdby": "Admin",
                                                                                          "state": "INACTIVE"}]
                                                                                 })):
            try:
                if 'transactions' not in transaction_data \
                        or not isinstance(transaction_data['transactions'], list):
                    return JSONResponse(content={'error': 'Invalid transactions format!'}, status_code=400)
                real_trans = transaction_data['transactions']

                # we need to check if transactions with such IDs already exist
                for trans in real_trans:
                    if ORM.Transaction.select().where(
                            ORM.Transaction.transactionid == trans['transactionid']):
                        return JSONResponse(
                            content={'error': f"Transaction with ID {trans['transactionid']} already exists!"},
                            status_code=409)

                ORM.Transaction.insert_many(real_trans).execute()
                return JSONResponse(content={'message': f"Transaction(s) created successfully!"})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating transaction: {e}'}, status_code=500)

        @app.post("/transactions/{transaction_id}/steps")
        async def create_transaction_step(
                transaction_id: str = Path(..., example="ffffffef-da62-4fed-8d46-c7d6baf80eb3"),
                step_data: dict = Body(..., example={"steps":
                                                         [{"stepid": "ffffffff-e707-4855-80cb-172ee4f2bfd8",
                                                           "transactionid": "ffffffef-da62-4fed-8d46-c7d6baf80eb3",
                                                           "name": "step-assistant",
                                                           "description": "An step to do transition and tulip",
                                                           "createddatetime": "2024-02-10 03:12:00.872079+00:00",
                                                           "createdby": "Admin"}]
                                                     })):
            try:
                self.validate_uuid4(transaction_id)

                if 'steps' not in step_data \
                        or not isinstance(step_data['steps'], list):
                    raise ValueError('Invalid steps format!')

                # we need to check if steps with such IDs already exist
                for step in step_data['steps']:
                    if ORM.Step_Info.select().where(ORM.Step_Info.stepid == step['stepid']):
                        return JSONResponse(content={'error': f"Step with ID {step['stepid']} already exists!"},
                                            status_code=409)

                ORM.Step_Info.insert_many(step_data['steps']).execute()
                return JSONResponse(content={'message': f"Step(s) added to transaction {transaction_id} successfully!"})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating step: {e}'}, status_code=500)

        # WARNING: here we have additional array 'step_runs' inside transaction run
        @app.post("/transactions/{transaction_id}/runs")
        async def create_transaction_run(
                transaction_id: str = Path(..., example="ffffffef-da62-4fed-8d46-c7d6baf80eb3"),
                runs_data: dict = Body(..., example={"runs":
                                                         [{"transactionrunid": "ffffffff-a086-43c0-b8b1-7658181d3204",
                                                           "transactionid": "ffffffef-da62-4fed-8d46-c7d6baf80eb3",
                                                           "runstart": "2024-02-14 17:29:28.198530",
                                                           "runend": "2024-02-14 17:29:28.542531",
                                                           "runresult": "OK",
                                                           "errorcode": 0,
                                                           "logid": "e27383c7-9473-454e-8bf0-c985c64cee42",
                                                           "step_runs": [{
                                                               "steprunid": "ffffffff-5e33-4d88-9ae8-1aa7aa556066",
                                                               "stepid": "ffffffff-e707-4855-80cb-172ee4f2bfd8",
                                                               "transactionrunid": "8f575292-a086-43c0-b8b1-7658181d3204",
                                                               "runstart": "2024-02-14 17:29:28.198543",
                                                               "runend": "2024-02-14 17:29:28.494544",
                                                               "runresult": "OK",
                                                               "logid": "e27383c7-9473-454e-8bf0-c985c64cee42",
                                                               "screenshotid": "c903c15a-0ee5-4f6a-b0e4-fd1d0a3d27c6",
                                                               "errorcode": 0
                                                           }]
                                                         }]
                                                     })):
            try:
                step_runs = []
                self.validate_uuid4(transaction_id)

                if not 'runs' in runs_data or not isinstance(runs_data['runs'], list):
                    raise ValueError('Invalid run format!')

                # we need to check if runs with such IDs already exist
                for run_index in range(len(runs_data['runs'])):
                    run = runs_data['runs'][run_index]

                    if ORM.Transaction_Run.select(). \
                            where(ORM.Transaction_Run.transactionrunid == run['transactionrunid']):
                        return JSONResponse(content={'error': f"Run with ID {run['transactionrunid']} already exists!"},
                                            status_code=409)

                    # same for step_runs
                    if not 'step_runs' in run or not isinstance(run['step_runs'], list):
                        raise ValueError('Invalid step runs format!')

                    current_step_runs = runs_data['runs'][run_index].pop('step_runs')
                    if not current_step_runs:
                        raise ValueError('Step runs cannot be empty!')
                    # also we need to check test runs for existing step IDs and step_runs responds step in transaction, but it takes too many time

                    step_runs.extend(current_step_runs)

                ORM.Transaction_Run.insert_many(runs_data['runs']).execute()
                ORM.Step_Run.insert_many(step_runs).execute()
                return JSONResponse(content={'message': f"Run(s) added to transaction {transaction_id} successfully!"})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating run: {e}'}, status_code=500)
