from fastapi import Body
from starlette.responses import JSONResponse

import orm.postgres as ORM # for now only Postgres is supported

from api.core import APICore, app


class GET(APICore):
    def get_base_data(self, table, filter_body):
        page = filter_body.pop('page', -1)
        per_page = filter_body.pop('per_page', -1)

        try:
            start_date = self.str_to_datetime(filter_body.pop('start'))
            end_date = self.str_to_datetime(filter_body.pop('end'))

            if start_date and end_date:
                if hasattr(table, 'runstart'):  # run table
                    rows = table.select().where(table.runstart >= start_date,
                                                table.runend <= end_date)
                else:
                    rows = ORM.Robots.select().where(table.createddatetime >= start_date,
                                                     table.createddatetime <= end_date)
            else:
                raise KeyError
        except KeyError:
            rows = table.select()

        for key, value in filter_body.items():
            if not hasattr(table, key):
                pass  # possibly not popped dynamic flag
            field = getattr(table, key)
            if isinstance(value, list):
                rows = rows.where(field << value)  # Peewee-specific 'in' equivalent
            else:
                rows = rows.where(field == value)

        return self.extract_page(rows, page, per_page)

    def __init__(self):
        super().__init__()

        @app.get("/robots", tags=['Read data'])
        async def get_robots(filter_body: dict = Body({}, openapi_examples={
            'Filter by city': {
                'description': 'Find robots located in a specific city',
                'value': {"city": "New York"}
            },
            'Filter by name and city': {
                'description': 'Find robots by name located in a specific city',
                'value': {"name": "RoboX", "city": "Tokyo"}
            },
            'Filter by datetime and city': {
                'description': 'Find robots created within a specific datetime range',
                'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59", "city": "Moscow"}
            },
            'Pagination': {
                'description': 'Get first 5 robots',
                'value': {"page": 1, "per_page": 5}
            }
        })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Robots, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'robots': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting robots: {e}'}, status_code=500)

        @app.get("/robots/{robot_id}", tags=['Read data'])
        async def get_robot_by_id(robot_id: str):
            try:
                self.validate_uuid4(robot_id)
                robot = ORM.Robots.get(ORM.Robots.robotid == robot_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(robot.__dict__)]
                return JSONResponse(content={'robot': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting robot by id: {e}'}, status_code=500)

        @app.get("/processes", tags=['Read data'])
        async def get_processes(filter_body: dict = Body({}, openapi_examples={
            'Filter by name': {
                'description': 'Find processes by name',
                'value': {"name": "Process 1"}
            },
            'Filter by datetime and creator': {
                'description': 'Find processes created within a specific datetime range',
                'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59", "createdby": "Admin"}
            },
            'Pagination': {
                'description': 'Get first 5 processes',
                'value': {"page": 1, "per_page": 5}
            }
        })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Process, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'processes': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting processes: {e}'}, status_code=500)

        @app.get("/processes/{process_id}", tags=['Read data'])
        async def get_process_by_id(process_id: str):
            try:
                self.validate_uuid4(process_id)
                process = ORM.Process.get(ORM.Process.processid == process_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(process.__dict__)]
                return JSONResponse(content={'process': self.json_reserialize(subresult)})
            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting process by id: {e}'}, status_code=500)

        @app.get("/services", tags=['Read data'])
        async def get_services(filter_body: dict = Body({}, openapi_examples={
            'Filter by process ID': {
                'description': 'Find services belonging to a specific process',
                'value': {"processid": "fbac34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b"}
            },
            'Filter by name and state': {
                'description': 'Find services by name with a specific state',
                'value': {"name": "ServiceX", "state": "ACTIVE"}
            },
            'Datetime filtering': {
                'description': 'Find services created within a specific datetime range',
                'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59"}
            },
            'Pagination': {
                'description': 'Get first 10 services',
                'value': {"page": 1, "per_page": 10}
            }
        })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Service, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'services': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting services: {e}'}, status_code=500)

        @app.get("/services/{service_id}", tags=['Read data'])
        async def get_service_by_id(service_id: str):
            try:
                self.validate_uuid4(service_id)
                service = ORM.Service.get(ORM.Service.serviceid == service_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(service.__dict__)]
                return JSONResponse(content={'service': self.json_reserialize(subresult)})
            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting service by id: {e}'}, status_code=500)

        @app.get("/transactions", tags=['Read data'])
        async def get_transactions(filter_body: dict = Body({}, openapi_examples={
            'Filter by service ID': {
                'description': 'Find transactions related to a specific service',
                'value': {"serviceid": "fab34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b"}
            },
            'Datetime filtering': {
                'description': 'Find transactions created within a specific datetime range',
                'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59"}
            },
            'Pagination': {
                'description': 'Get first 10 transactions related to a specific service',
                'value': {"serviceid": "fab34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b", "page": 1, "per_page": 10}
            }
        })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Transaction, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'transactions': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transactions: {e}'}, status_code=500)

        @app.get("/transactions/{transaction_id}", tags=['Read data'])
        async def get_transaction_by_id(transaction_id: str):
            try:
                self.validate_uuid4(transaction_id)
                transaction = ORM.Transaction.get(ORM.Transaction.transactionid == transaction_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(transaction.__dict__)]
                return JSONResponse(content={'transaction': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transaction by id: {e}'}, status_code=500)

        @app.get("/steps", tags=['Read data'])
        async def get_steps(filter_body: dict = Body({}, openapi_examples={
            'Filter by transaction ID': {
                'description': 'Find steps belonging to a specific transaction',
                'value': {"transactionid": "ab2c34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b"}
            },
            'Datetime filtering': {
                'description': 'Find steps created within a specific datetime range',
                'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59"}
            },
            'Pagination': {
                'description': 'Get first 5 steps related to a specific transaction',
                'value': {"transactionid": "ab2c34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b", "page": 1, "per_page": 5}
            }
        })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Step_Info, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'steps': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting steps: {e}'}, status_code=500)

        @app.get("/steps/{step_id}", tags=['Read data'])
        async def get_step_by_id(step_id: str):
            try:
                self.validate_uuid4(step_id)
                step = ORM.Step_Info.get(ORM.Step_Info.stepid == step_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(step.__dict__)]
                return JSONResponse(content={'step': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting step by id: {e}'}, status_code=500)

        # transactions runs
        @app.get("/runs", tags=['Read data'])
        async def get_runs(filter_body: dict = Body({}, openapi_examples={
            'Filter by transaction ID': {
                'description': 'Find transaction runs belonging to a specific transaction',
                'value': {"transactionid": "ab2c34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b"}
            },
            'Datetime filtering': {
                'description': 'Find transaction runs that started and ended within a specific datetime range',
                'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59"}
            },
            'Pagination': {
                'description': 'Get 11-20 runs related to a specific transaction ordered by descending end date',
                'value': {"transactionid": "ab2c34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b", "page": 2, "per_page": 10}
            }
        })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Transaction_Run, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting runs: {e}'}, status_code=500)

        @app.get("/runs/{run_id}", tags=['Read data'])
        async def get_run_by_id(run_id: str):
            try:
                self.validate_uuid4(run_id)
                run = ORM.Transaction_Run.get(ORM.Transaction_Run.transactionrunid == run_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(run.__dict__)]
                return JSONResponse(content={'run': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting run by id: {e}'}, status_code=500)

        # steps runs, connection by transactionrunid and stepid
        @app.get("/step_runs", tags=['Read data'])
        async def get_step_runs(filter_body: dict = Body({}, openapi_examples={
                'Filter by transaction run': {
                    'description': 'Find all step runs with equal transaction run ID',
                    'value': {"transactionrunid": "fbac34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b"}
                },
                'Filter by step': {
                    'description': 'Find all step runs with equal step ID',
                    'value': {"stepid": "fbac34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b"}
                },
                'Datetime filtering': {
                    'description': 'Find step runs that started and ended within a specific datetime range',
                    'value': {"start": "2023-01-01T00:00:00", "end": "2023-12-31T23:59:59"}
                },
                'Pagination': {
                    'description': 'Get first 5 step runs related to a specific transaction run',
                    'value': {"transactionrunid": "fbac34a0-0b3b-4b3b-8b3b-0b3b4b3b4b3b", "page": 1, "per_page": 5}
                }
            })):
            try:
                # pop needed keys from filter body for dynamic postprocessing
                subresult = self.get_base_data(ORM.Step_Run, filter_body)
                # run dynamic postprocessing here TODO
                return JSONResponse(content={'step_runs': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting step runs: {e}'}, status_code=500)

        @app.get("/step_runs/{step_run_id}", tags=['Read data'])
        async def get_step_run_by_id(step_run_id: str):
            try:
                self.validate_uuid4(step_run_id)
                step_run = ORM.Step_Run.get(ORM.Step_Run.steprunid == step_run_id)
                subresult = [ORM.BaseModel.extract_data_from_select_dict(step_run.__dict__)]
                return JSONResponse(content={'step_run': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting step run by id: {e}'}, status_code=500)
