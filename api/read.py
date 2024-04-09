import datetime

from fastapi import Body
from starlette.responses import JSONResponse

from peewee import fn, SQL
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

    @staticmethod
    def get_runs_for_list(ids, start, end, idtype='transactionid', table='Transaction_Run'):
        result = {'ok': 0, 'warning': 0, 'fail': 0}
        if isinstance(ids, dict):
            lst = list(ids.keys())
        elif isinstance(ids, list):
            lst = ids
        else:
            raise TypeError('Invalid type for IDs list')

        for r in result:
            result[r] = getattr(ORM, table).select()\
                .where(getattr(getattr(ORM, table), idtype) << lst)\
                .where(getattr(ORM, table).runresult == r.upper())\
                .where(getattr(ORM, table).runstart >= start)\
                .where(getattr(ORM, table).runend <= end)\
            .count()

        # count avg/min/max for 'runend - runstart'
        for func in ['avg', 'min', 'max']:
            try:
                result[func] = getattr(ORM, table).select(getattr(fn, func.upper())
                    (getattr(ORM, table).runend - getattr(ORM, table).runstart))\
                    .where(getattr(getattr(ORM, table), idtype) << lst)\
                    .where(getattr(ORM, table).runstart >= start)\
                    .where(getattr(ORM, table).runend <= end).scalar().total_seconds()
            except AttributeError: # no runs on required range
                result[func] = 0

        result['total'] = result['ok'] + result['warning'] + result['fail']
        result['sla'] = (result['ok'] / result['total']) * 100 if result['total'] else 0
        return result

    def date_logic(self, filter_body):
        now = datetime.datetime.now()
        backmon = now - datetime.timedelta(days=now.weekday())
        monday = datetime.datetime(backmon.year, backmon.month, backmon.day, 0, 0, 0)

        midnight = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)  # of current day
        start_date = self.str_to_datetime(filter_body.pop('start', None), monday)
        end_date = self.str_to_datetime(filter_body.pop('end', None), now)

        if start_date == monday and end_date == midnight:
            diff = datetime.timedelta(days=7)
        else:
            diff = end_date - start_date
        prev_start = start_date - diff

        return now, monday, midnight, start_date, end_date, prev_start

    @staticmethod
    def runtime_filtering(id, table, min=None, max=None, table_name='Transaction_Run', idtype='robotid'):
        min_sql = SQL(f"INTERVAL '{min} seconds'") if min else None
        max_sql = SQL(f"INTERVAL '{max} seconds'") if max else None
        if min_sql and max_sql:
            rows = table.select()\
                    .where(getattr(getattr(ORM, table_name), idtype) == id)\
                    .where(getattr(ORM, table_name).runend - getattr(ORM, table_name).runstart >= min_sql)\
                    .where(getattr(ORM, table_name).runend - getattr(ORM, table_name).runstart <= max_sql)\
                    .count()
        elif min_sql:
            rows = table.select()\
                    .where(getattr(getattr(ORM, table_name), idtype) == id)\
                    .where(getattr(ORM, table_name).runend - getattr(ORM, table_name).runstart >= min_sql)\
                    .count()
        elif max_sql:
            rows = table.select()\
                    .where(getattr(getattr(ORM, table_name), idtype) == id)\
                    .where(getattr(ORM, table_name).runend - getattr(ORM, table_name).runstart <= max_sql)\
                    .count()
        else:
            rows = table.select()\
                    .where(getattr(getattr(ORM, table_name), idtype) == id)\
                    .count()

        return rows

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
                subresult = self.get_base_data(ORM.Robots, filter_body)
                return JSONResponse(content={'robots': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting robots: {e}'}, status_code=500)

        @app.get("/robots/{robot_id}", tags=['Read data'])
        async def get_robot_by_id(robot_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                self.validate_uuid4(robot_id)
                robot = ORM.Robots.get(ORM.Robots.robotid == robot_id)
                subresult = ORM.BaseModel.extract_data_from_select_dict(robot.__dict__)

                # step 1 - get list of runs for robot (directly by 'robotid')
                runs_cur = self.get_runs_for_list([robot_id], start_date, end_date, idtype='robotid')
                subresult['fail_cur'] = runs_cur['fail']
                subresult['sla_cur'] = runs_cur['sla']

                runs_prev = self.get_runs_for_list([robot_id], prev_start, start_date, idtype='robotid')
                subresult['sla_prev'] = runs_prev['sla']

                runs_daily = self.get_runs_for_list([robot_id], midnight, now, idtype='robotid')
                subresult['sla_daily'] = runs_daily['sla']

                # step 2 - run day-by-day starting from start_date with time dropped to 00:00:00
                subresult['runs_daily'] = {}
                day = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
                one_day_diff = datetime.timedelta(days=1)
                while day < end_date:
                    runs = self.get_runs_for_list([robot_id], day, day + one_day_diff, idtype='robotid')
                    subresult['runs_daily'][day.strftime('%Y-%m-%d')] = runs
                    day += one_day_diff

                # step 3 - create list of unique transaction IDs based on list of run IDs
                runs = ORM.Transaction_Run.select(ORM.Transaction_Run.transactionid)\
                    .where(ORM.Transaction_Run.robotid == robot_id)
                transaction_ids = {str(run.transactionid): {} for run in runs}

                # step 4 - get runs for all transactions via method and count SLA
                subresult['trans_ok'] = 0
                subresult['trans_warning'] = 0
                subresult['trans_fail'] = 0
                for tid in transaction_ids:
                    runs = self.get_runs_for_list([tid], start_date, end_date)
                    if runs['fail']:
                        subresult['trans_fail'] += 1
                    elif runs['warning']:
                        subresult['trans_warning'] += 1
                    else:
                        subresult['trans_ok'] += 1
                    transaction_ids[tid] |= runs

                # step 5 - sort transactions by ascending SLA
                subresult['transactions'] = dict(sorted(transaction_ids.items(), key=lambda x: x[1]['sla']))

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
                subresult = self.get_base_data(ORM.Process, filter_body)
                return JSONResponse(content={'processes': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting processes: {e}'}, status_code=500)

        @app.get("/processes/{process_id}", tags=['Read data'])
        async def get_process_by_id(process_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                self.validate_uuid4(process_id)
                process = ORM.Process.get(ORM.Process.processid == process_id)
                subresult = ORM.BaseModel.extract_data_from_select_dict(process.__dict__)

                # step 0 - prepare variables in subresult
                subresult['trans_daily'] = {}

                # step 1 - get list of services for process
                services = ORM.Service.select()\
                    .where(ORM.Service.processid == process_id)
                service_ids = {str(service.serviceid): {} for service in services}

                global_trans_ids = []
                for service_id in service_ids:
                    # step 2 - get list of transactions for each service
                    transactions = ORM.Transaction.select(ORM.Transaction.transactionid)\
                        .where(ORM.Transaction.serviceid == service_id)
                    transaction_ids = [str(transaction.transactionid) for transaction in transactions]
                    global_trans_ids.extend(transaction_ids)

                    # step 3 - select OK, WARNING, FAIL only for current date range
                    runs = self.get_runs_for_list(transaction_ids, start_date, end_date)
                    service_ids[service_id] |= runs # update dict with runs

                # step 4 - sort services by ascending SLA
                subresult['services'] = dict(sorted(service_ids.items(), key=lambda x: x[1]['sla']))

                # step 5 - get SLA for current, prev and daily
                runs_cur = self.get_runs_for_list(global_trans_ids, start_date, end_date)
                subresult['fail_cur'] = runs_cur['fail']
                subresult['sla_cur'] = runs_cur['sla']

                runs_prev = self.get_runs_for_list(global_trans_ids, prev_start, start_date)
                subresult['sla_prev'] = runs_prev['sla']

                runs_daily = self.get_runs_for_list(global_trans_ids, midnight, now)
                subresult['sla_daily'] = runs_daily['sla']

                # step 6 - run day-by-day starting from start_date with time dropped to 00:00:00
                day = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
                one_day_diff = datetime.timedelta(days=1)
                while day < end_date:
                    runs = self.get_runs_for_list(global_trans_ids, day, day + one_day_diff)
                    subresult['trans_daily'][day.strftime('%Y-%m-%d')] = runs
                    day += one_day_diff

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
                subresult = self.get_base_data(ORM.Service, filter_body)
                return JSONResponse(content={'services': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting services: {e}'}, status_code=500)

        @app.get("/services/{service_id}", tags=['Read data'])
        async def get_service_by_id(service_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                self.validate_uuid4(service_id)
                service = ORM.Service.get(ORM.Service.serviceid == service_id)
                subresult = ORM.BaseModel.extract_data_from_select_dict(service.__dict__)

                # step 1 - get list of transactions for service
                transactions = ORM.Transaction.select(ORM.Transaction.transactionid)\
                    .where(ORM.Transaction.serviceid == service_id)
                transaction_ids = {str(transaction.transactionid): {} for transaction in transactions}

                # step 2 - get runs for all transactions via method and count SLA
                runs_cur = self.get_runs_for_list(transaction_ids, start_date, end_date)
                subresult['fail_cur'] = runs_cur['fail']
                subresult['sla_cur'] = runs_cur['sla']

                runs_prev = self.get_runs_for_list(transaction_ids, prev_start, start_date)
                subresult['sla_prev'] = runs_prev['sla']

                runs_daily = self.get_runs_for_list(transaction_ids, midnight, now)
                subresult['sla_daily'] = runs_daily['sla']

                # step 3 - for each transaction check if there're any WARNING or FAIL runs
                subresult['trans_ok'] = 0
                subresult['trans_warning'] = 0
                subresult['trans_fail'] = 0
                subresult['trans_daily'] = {}
                for tid in transaction_ids:
                    runs = self.get_runs_for_list([tid], start_date, end_date)
                    if runs['fail']:
                        subresult['trans_fail'] += 1
                    elif runs['warning']:
                        subresult['trans_warning'] += 1
                    else:
                        subresult['trans_ok'] += 1
                    transaction_ids[tid] |= runs

                # step 4 - sort transactions by ascending SLA
                subresult['transactions'] = dict(sorted(transaction_ids.items(), key=lambda x: x[1]['sla']))

                # step 5 - run day-by-day starting from start_date with time dropped to 00:00:00
                day = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
                one_day_diff = datetime.timedelta(days=1)
                while day < end_date:
                    runs = self.get_runs_for_list(transaction_ids, day, day + one_day_diff)
                    subresult['trans_daily'][day.strftime('%Y-%m-%d')] = runs
                    day += one_day_diff

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
                subresult = self.get_base_data(ORM.Transaction, filter_body)
                return JSONResponse(content={'transactions': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting transactions: {e}'}, status_code=500)

        @app.get("/transactions/{transaction_id}", tags=['Read data'])
        async def get_transaction_by_id(transaction_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                self.validate_uuid4(transaction_id)
                transaction = ORM.Transaction.get(ORM.Transaction.transactionid == transaction_id)
                subresult = ORM.BaseModel.extract_data_from_select_dict(transaction.__dict__)

                # step 1 - get list of runs for transaction
                runs_cur = self.get_runs_for_list([transaction_id], start_date, end_date)
                subresult['fail_cur'] = runs_cur['fail']
                subresult['sla_cur'] = runs_cur['sla']

                runs_prev = self.get_runs_for_list([transaction_id], prev_start, start_date)
                subresult['sla_prev'] = runs_prev['sla']

                runs_daily = self.get_runs_for_list([transaction_id], midnight, now)
                subresult['sla_daily'] = runs_daily['sla']

                # step 2 - get list of robots for transaction
                robots = ORM.Transaction_Run.select(ORM.Transaction_Run.robotid)\
                    .where(ORM.Transaction_Run.transactionid == transaction_id)
                robot_ids = {str(robot.robotid): {} for robot in robots}

                # step 3 - get runs for all robots via method and count SLA
                for rid in robot_ids:
                    runs = self.get_runs_for_list([rid], start_date, end_date, idtype='robotid')
                    robot_ids[rid] |= runs
                    robot_ids[rid]['0-30'] = self.runtime_filtering(rid, ORM.Transaction_Run, max=30)
                    robot_ids[rid]['30-60'] = self.runtime_filtering(rid, ORM.Transaction_Run, min=30, max=60)
                    robot_ids[rid]['60-120'] = self.runtime_filtering(rid, ORM.Transaction_Run, min=60, max=120)
                    robot_ids[rid]['120-300'] = self.runtime_filtering(rid, ORM.Transaction_Run, min=120, max=300)
                    robot_ids[rid]['300+'] = self.runtime_filtering(rid, ORM.Transaction_Run, min=300)

                # step 4 - sort robots by ascending SLA
                subresult['robots'] = dict(sorted(robot_ids.items(), key=lambda x: x[1]['sla']))

                # step 5 - get list of steps for transaction
                steps = ORM.Step_Info.select(ORM.Step_Info.stepid)\
                    .where(ORM.Step_Info.transactionid == transaction_id)
                step_ids = {str(step.stepid): {} for step in steps}

                # step 6 - get runs for all steps via method and count SLA
                for sid in step_ids:
                    runs = self.get_runs_for_list([sid], start_date, end_date, idtype='stepid', table='Step_Run')
                    step_ids[sid] |= runs

                # step 7 - sort steps by ascending SLA
                subresult['steps'] = dict(sorted(step_ids.items(), key=lambda x: x[1]['sla']))

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
                subresult = self.get_base_data(ORM.Step_Info, filter_body)
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
                subresult = self.get_base_data(ORM.Transaction_Run, filter_body)
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
                subresult = self.get_base_data(ORM.Step_Run, filter_body)
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
