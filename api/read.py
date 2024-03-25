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


        @app.get("/robots")
        async def get_robots():
            try:
                robots = ORM.Robots.select()
                subresult = [ORM.BaseModel.extract_data_from_select_dict(robot.__dict__)
                             for robot in robots]
                return JSONResponse(content={'robots': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting robots: {e}'}, status_code=500)


        @app.get("/services")
        async def get_services():
            try:
                services = ORM.Services.select()
                subresult = [ORM.BaseModel.extract_data_from_select_dict(service.__dict__)
                             for service in services]
                return JSONResponse(content={'services': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting services: {e}'}, status_code=500)


        @app.get("/services/{service_id}")
        async def get_service_by_id(service_id: str):
            try:
                self.validate_uuid4(service_id)

                services = ORM.Services.select().where(ORM.Services.serviceid == service_id)
                if not services:
                    return JSONResponse(content={'error': 'Service not found!'}, status_code=404)

                result_service = ORM.BaseModel.extract_data_from_select_dict(services[0].__dict__)
                return JSONResponse(content={'services': [self.json_reserialize(result_service)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting service: {e}'}, status_code=500)


        @app.get("/services/{service_id}/business_processes")
        @app.get("/business_processes")
        async def get_service_business_processes(service_id: str = ''):
            try:
                if service_id:
                    self.validate_uuid4(service_id)
                    business_processes = ORM.Business_Process.select().where(
                        ORM.Business_Process.serviceid == service_id)
                else:
                    business_processes = ORM.Business_Process.select()
                if service_id and not business_processes:
                    return JSONResponse(content={'error': 'Business processes not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(process.__dict__)
                             for process in business_processes]
                return JSONResponse(content={'business_processes': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting business processes: {e}'}, status_code=500)


        @app.get("/services/{service_id}/business_processes/{process_id}")
        @app.get("/business_processes/{process_id}")
        async def get_business_process_by_id(process_id: str, service_id: str = ''):
            try:
                if service_id:
                    self.validate_uuid4(service_id)
                self.validate_uuid4(process_id)

                process = ORM.Business_Process.select().where(ORM.Business_Process.processid == process_id)[0]
                if not process:
                    return JSONResponse(content={'error': 'Business process not found!'}, status_code=404)

                result_process = ORM.BaseModel.extract_data_from_select_dict(process.__dict__)
                return JSONResponse(content={'business_processes': [self.json_reserialize(result_process)]})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting business process: {e}'}, status_code=500)


        @app.get("/services/{service_id}/business_processes/{process_id}/transactions")
        @app.get("/business_processes/{process_id}/transactions")
        @app.get("/transactions")
        async def get_transactions(process_id: str = ''):
            try:
                if process_id:
                    self.validate_uuid4(process_id)
                    transactions = ORM.Transaction.select().where(ORM.Transaction.processid == process_id)
                else:
                    transactions = ORM.Transaction.select()

                if process_id and not transactions:
                    return JSONResponse(content={'error': 'Transactions not found!'}, status_code=404)

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
        @app.get("/steps")
        async def get_transaction_steps(transaction_id: str = ''):
            try:
                # make it possible to get list of ALL steps (not only for single transaction) for MVP
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                    transaction_steps = ORM.Step_Info.select().where(
                        ORM.Step_Info.transactionid == transaction_id)
                else:
                    transaction_steps = ORM.Step_Info.select()

                if transaction_id and not transaction_steps:
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

                step_runs = ORM.Step_Run.select()\
                    .where(ORM.Step_Run.stepid == step_id).order_by(ORM.Step_Run.runend)
                if not step_runs:
                    return JSONResponse(content={'error': 'Step runs not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(run.__dict__)
                             for run in step_runs][::-1] # Clickhouse doesn't support desc() in ORM :(
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
        @app.get("/runs")
        async def get_transaction_runs(transaction_id: str = ''):
            try:
                # make it possible to get list of ALL runs (not only for single transaction)
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                    transaction_runs = ORM.Transaction_Run.select().where(
                        ORM.Transaction_Run.transactionid == transaction_id).order_by(ORM.Transaction_Run.runend)
                else:
                    transaction_runs = ORM.Transaction_Run.select().order_by(ORM.Transaction_Run.runend)

                if transaction_id and not transaction_runs:
                    return JSONResponse(content={'error': 'Transaction runs not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(run.__dict__)
                             for run in transaction_runs][::-1] # Clickhouse doesn't support desc() in ORM :(
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

                run_steps = ORM.Step_Run.select()\
                    .where(ORM.Step_Run.transactionrunid == run_id).order_by(ORM.Step_Run.runend)
                if not run_steps:
                    return JSONResponse(content={'error': 'Run steps not found!'}, status_code=404)

                subresult = [ORM.BaseModel.extract_data_from_select_dict(step.__dict__)
                             for step in run_steps][::-1] # Clickhouse doesn't support desc() in ORM :(
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
