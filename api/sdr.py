import datetime

from fastapi import Body
from starlette.responses import JSONResponse

from api.base_read import BaseGET
from api.core import app
from orm import postgres as ORM


class SingleGET(BaseGET):
    def __init__(self):
        super().__init__()

        @app.get("/robots/{robot_id}", tags=['Read dynamic data'])
        async def get_robot_by_id(robot_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)
                sublists = filter_body.pop('sublists', False)

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

                # we should be able to not get sublists when not needed
                if not sublists:
                    return JSONResponse(content={'robot': self.json_reserialize(subresult)})

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
                    transaction_ids[tid]['name'] = ORM.Transaction.select(ORM.Transaction.name)\
                        .where(ORM.Transaction.transactionid == tid).scalar()

                # step 5 - sort transactions by ascending SLA
                subresult['transactions'] = dict(sorted(transaction_ids.items(), key=lambda x: x[1]['sla']))

                return JSONResponse(content={'robot': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting robot by id: {e}'}, status_code=500)

        @app.get("/processes/{process_id}", tags=['Read dynamic data'])
        async def get_process_by_id(process_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)
                sublists = filter_body.pop('sublists', False)

                self.validate_uuid4(process_id)
                process = ORM.Process.get(ORM.Process.processid == process_id)
                subresult = ORM.BaseModel.extract_data_from_select_dict(process.__dict__)

                # step 1 - get list of services for process
                services = ORM.Service.select()\
                    .where(ORM.Service.processid == process_id)
                service_ids = {str(service.serviceid): {} for service in services}

                # step 1.1 - get list of transactions for each service in list
                global_trans_ids = list(ORM.Transaction.select(ORM.Transaction.transactionid)\
                    .where(ORM.Transaction.serviceid << list(service_ids.keys())))

                # step 2 - get SLA for current, prev and daily
                runs_cur = self.get_runs_for_list(global_trans_ids, start_date, end_date)
                subresult['fail_cur'] = runs_cur['fail']
                subresult['sla_cur'] = runs_cur['sla']

                runs_prev = self.get_runs_for_list(global_trans_ids, prev_start, start_date)
                subresult['sla_prev'] = runs_prev['sla']

                runs_daily = self.get_runs_for_list(global_trans_ids, midnight, now)
                subresult['sla_daily'] = runs_daily['sla']

                # we should be able to not get sublists when not needed
                if not sublists:
                    return JSONResponse(content={'process': self.json_reserialize(subresult)})

                for service_id in service_ids:
                    # step 3 - get list of transactions for each service
                    transactions = ORM.Transaction.select(ORM.Transaction.transactionid)\
                        .where(ORM.Transaction.serviceid == service_id)
                    transaction_ids = [str(transaction.transactionid) for transaction in transactions]

                    # step 4 - select OK, WARNING, FAIL only for current date range
                    runs = self.get_runs_for_list(transaction_ids, start_date, end_date)
                    service_ids[service_id] |= runs # update dict with runs

                # step 5 - sort services by ascending SLA
                subresult['services'] = dict(sorted(service_ids.items(), key=lambda x: x[1]['sla']))

                # step 6 - run day-by-day starting from start_date with time dropped to 00:00:00
                subresult['trans_daily'] = {}
                day = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
                one_day_diff = datetime.timedelta(days=1)
                while day < end_date:
                    runs = self.get_runs_for_list(global_trans_ids, day, day + one_day_diff)
                    subresult['trans_daily'][day.strftime('%Y-%m-%d')] = runs
                    day += one_day_diff

                return JSONResponse(content={'process': self.json_reserialize(subresult)})
            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting process by id: {e}'}, status_code=500)

        @app.get("/services/{service_id}", tags=['Read dynamic data'])
        async def get_service_by_id(service_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)
                sublists = filter_body.pop('sublists', False)

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

                # we should be able to not get sublists when not needed
                if not sublists:
                    return JSONResponse(content={'service': self.json_reserialize(subresult)})

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

        @app.get("/transactions/{transaction_id}", tags=['Read dynamic data'])
        async def get_transaction_by_id(transaction_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)
                sublists = filter_body.pop('sublists', False)

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

                # we should be able to not get sublists when not needed
                if not sublists:
                    return JSONResponse(content={'transaction': self.json_reserialize(subresult)})

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

        @app.get("/runs/{run_id}", tags=['Read dynamic data'])
        async def get_run_by_id(run_id: str, filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                self.validate_uuid4(run_id)
                run = ORM.Transaction_Run.get(ORM.Transaction_Run.transactionrunid == run_id)
                subresult = ORM.BaseModel.extract_data_from_select_dict(run.__dict__)
                # remove base64 encoded log and screenshot
                subresult.pop('log', None)
                subresult.pop('screenshot', None)

                # step 1 - get coefficients from method
                runs_data = self.get_runs_for_list([run.transactionid], start_date, end_date)
                subresult |= runs_data

                # step 2 - get all robots running current transaction
                runs = ORM.Transaction_Run.select()\
                    .where(ORM.Transaction_Run.transactionid == run.transactionid)
                robot_ids = {str(run.robotid): {} for run in runs}

                # step 3 - get runs for all robots via method and count SLA
                for rid in robot_ids:
                    rns = self.get_runs_for_list([rid], start_date, end_date, idtype='robotid')
                    robot_ids[rid] |= rns

                # step 4 - sort robots by ascending SLA
                subresult['robots'] = dict(sorted(robot_ids.items(), key=lambda x: x[1]['sla']))

                return JSONResponse(content={'run': self.json_reserialize(subresult)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting run by id: {e}'}, status_code=500)

        @app.get("/global_sla", tags=['Read dynamic data'])
        async def get_global_sla(filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                # step 1 - get all transactions
                transactions = ORM.Transaction.select(ORM.Transaction.transactionid)
                transaction_ids = [str(transaction.transactionid) for transaction in transactions]

                # step 2 - get SLA for current, prev and daily
                subresult = {}
                runs_cur = self.get_runs_for_list(transaction_ids, start_date, end_date)
                subresult['fail_cur'] = runs_cur['fail']
                subresult['sla_cur'] = runs_cur['sla']

                runs_prev = self.get_runs_for_list(transaction_ids, prev_start, start_date)
                subresult['sla_prev'] = runs_prev['sla']

                runs_daily = self.get_runs_for_list(transaction_ids, midnight, now)
                subresult['sla_daily'] = runs_daily['sla']

                return JSONResponse(content={'global_sla': subresult})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting global SLAs: {e}'}, status_code=500)
