import uuid
from datetime import datetime

from fastapi import Body
from starlette.responses import JSONResponse

import orm.postgres as ORM

from api.core import APICore, app


class POST(APICore):
    def __init__(self):
        super().__init__()

        @app.post("/robots", tags=['Add new data'])
        async def create_robot(robot_data: dict = Body(..., example={"robots":
                                                                        [{"name": "robot-windows",
                                                                             "city": "New York",
                                                                             "latitude": 40.7128,
                                                                             "longitude": -74.0060,
                                                                             "createddatetime": "2024-02-10 03:12:00.841588",
                                                                             "createdby": "Admin"}]
                                                                     })):
                try:
                    if 'robots' not in robot_data or not isinstance(robot_data['robots'], list):
                        return JSONResponse(content={'error': 'Invalid robots format!'}, status_code=400)
                    real_robots = robot_data['robots']

                    # generate UUID for each robot and reparse datetime fields to Peewee compatible format 'YYYY-MM-DD HH:MM:SS.SSSSSS'
                    uuids = []
                    for robot in real_robots:
                        robot['robotid'] = uuid.uuid4()
                        uuids.append(robot['robotid'])

                        try:
                            extracted_datetime = self.str_to_datetime(robot['createddatetime'])
                            robot['createddatetime'] = datetime.strftime(extracted_datetime, '%Y-%m-%d %H:%M:%S.%f')
                        except Exception:
                            # use now() if datetime is invalid
                            robot['createddatetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                    ORM.Robots.insert_many(real_robots).execute()
                    return JSONResponse(content={'message': f"Robot(s) created successfully!", 'ids': self.json_reserialize(uuids)})

                except Exception as e:
                    return JSONResponse(content={'error': f'Error while creating robot: {e}'}, status_code=500)

        @app.post("/processes", tags=['Add new data'])
        async def create_process(process_data: dict = Body(..., example={"processes":
                                                                            [{"name": "process-1",
                                                                                "description": "process for testing",
                                                                                "createddatetime": "2024-02-10 03:12:00.841588",
                                                                                "createdby": "Admin"}]
                                                                         })):
                try:
                    if 'processes' not in process_data or not isinstance(process_data['processes'], list):
                        return JSONResponse(content={'error': 'Invalid processes format!'}, status_code=400)
                    real_processes = process_data['processes']

                    # generate UUID for each process
                    uuids = []
                    for process in real_processes:
                        process['processid'] = uuid.uuid4()
                        uuids.append(process['processid'])

                        try:
                            extracted_datetime = self.str_to_datetime(process['createddatetime'])
                            process['createddatetime'] = datetime.strftime(extracted_datetime, '%Y-%m-%d %H:%M:%S.%f')
                        except Exception:
                            process['createddatetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                    ORM.Process.insert_many(real_processes).execute()
                    return JSONResponse(content={'message': f"Process(es) created successfully!", 'ids': self.json_reserialize(uuids)})

                except Exception as e:
                    return JSONResponse(content={'error': f'Error while creating process(es): {e}'}, status_code=500)

        @app.post("/services", tags=['Add new data'])
        async def create_business_process(service_data: dict = Body(..., example={"services":
                                                                                       [{"processid": "ffffffff-5e33-4d88-9ae8-1aa7aa556066",
                                                                                         "name": "bp-1",
                                                                                         "description": "Service for testing",
                                                                                         "createddatetime": "2024-02-10 03:12:00.841588",
                                                                                         "createdby": "Admin"}]
                                                                                   })):
            try:
                if 'services' not in service_data or not isinstance(service_data['services'], list):
                    return JSONResponse(content={'error': 'Invalid services format!'}, status_code=400)
                real_services = service_data['services']

                # generate UUID for each service
                uuids = []
                for service in real_services:
                    service['serviceid'] = uuid.uuid4()
                    uuids.append(service['serviceid'])

                    try:
                        extracted_datetime = self.str_to_datetime(service['createddatetime'])
                        service['createddatetime'] = datetime.strftime(extracted_datetime, '%Y-%m-%d %H:%M:%S.%f')
                    except Exception:
                        service['createddatetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                ORM.Service.insert_many(real_services).execute()
                return JSONResponse(content={'message': f"Service(s) created successfully!", 'ids': self.json_reserialize(uuids)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating service(es): {e}'}, status_code=500)

        @app.post("/transactions", tags=['Add new data'])
        async def create_transaction(transaction_data: dict = Body(..., example={"transactions":
                                                                                     [{"serviceid": "fd2fffef-da62-4fff-8d46-c7d6baf80eb3",
                                                                                          "name": "tr-morning-faithful",
                                                                                          "description": "An awesome transaction tr-morning-faithful executed by robot robot-windows",
                                                                                          "createddatetime": "2024-02-10 03:12:00.841588",
                                                                                          "createdby": "Admin",
                                                                                          "state": "INACTIVE"}]
                                                                                 })):
            try:
                if 'transactions' not in transaction_data \
                        or not isinstance(transaction_data['transactions'], list):
                    return JSONResponse(content={'error': 'Invalid transactions format!'}, status_code=400)
                real_trans = transaction_data['transactions']

                # generate UUID for each transaction
                uuids = []
                for transaction in real_trans:
                    transaction['transactionid'] = uuid.uuid4()
                    uuids.append(transaction['transactionid'])

                    try:
                        extracted_datetime = self.str_to_datetime(transaction['createddatetime'])
                        transaction['createddatetime'] = datetime.strftime(extracted_datetime, '%Y-%m-%d %H:%M:%S.%f')
                    except Exception:
                        transaction['createddatetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                ORM.Transaction.insert_many(real_trans).execute()
                return JSONResponse(content={'message': f"Transaction(s) created successfully!", 'ids': self.json_reserialize(uuids)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating transaction: {e}'}, status_code=500)

        @app.post("/steps", tags=['Add new data'])
        async def create_transaction_step(step_data: dict = Body(..., example={"steps":
                                                         [{"transactionid": "ffffffef-da62-4fed-8d46-c7d6baf80eb3",
                                                           "name": "step-assistant",
                                                           "description": "An step to do transition and tulip",
                                                           "createddatetime": "2024-02-10 03:12:00.872079",
                                                           "createdby": "Admin"}]
                                                     })):
            try:
                if 'steps' not in step_data \
                        or not isinstance(step_data['steps'], list):
                    raise ValueError('Invalid steps format!')

                # generate UUID for each step
                uuids = []
                for step in step_data['steps']:
                    step['stepid'] = uuid.uuid4()
                    uuids.append(step['stepid'])

                    try:
                        extracted_datetime = self.str_to_datetime(step['createddatetime'])
                        step['createddatetime'] = datetime.strftime(extracted_datetime, '%Y-%m-%d %H:%M:%S.%f')
                    except Exception:
                        step['createddatetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                ORM.Step_Info.insert_many(step_data['steps']).execute()
                return JSONResponse(content={'message': f"Step(s) added successfully!", 'ids': self.json_reserialize(uuids)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating step: {e}'}, status_code=500)

        # WARNING: here we have additional array 'step_runs' inside transaction run
        @app.post("/runs", tags=['Add new data'])
        async def create_transaction_run(runs_data: dict = Body(..., example={"runs":
                                                         [{"transactionid": "ffffffef-da62-4fed-8d46-c7d6baf80eb3",
                                                           "robotid": "fd2fffef-da62-4fff-8d46-c7d6baf80eb3",
                                                           "runstart": "2024-02-14 17:29:28.198530",
                                                           "runend": "2024-02-14 17:29:28.542531",
                                                           "runresult": "OK",
                                                           "errorcode": 0,
                                                           "log": "BASE64 ENCODED STRING",
                                                           "screenshot": "BASE64 ENCODED STRING",
                                                           "step_runs": [{
                                                               "stepid": "ffffffff-e707-4855-80cb-172ee4f2bfd8",
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

                if not 'runs' in runs_data or not isinstance(runs_data['runs'], list):
                    raise ValueError('Invalid run format!')

                uuids = []
                for run_index in range(len(runs_data['runs'])):
                    run = runs_data['runs'][run_index]
                    run['transactionrunid'] = uuid.uuid4()
                    uuids.append(run['transactionrunid'])

                    try:
                        extracted_runstart = self.str_to_datetime(run['runstart'])
                        run['runstart'] = datetime.strftime(extracted_runstart, '%Y-%m-%d %H:%M:%S.%f')
                    except Exception:
                        run['runstart'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                    if not 'step_runs' in run or not isinstance(run['step_runs'], list):
                        raise ValueError('Invalid step runs format!')

                    current_step_runs = runs_data['runs'][run_index].pop('step_runs')
                    if not current_step_runs:
                        raise ValueError('Step runs cannot be empty!')

                    # for each step run generate UUID and add transactionrunid
                    for step_run in current_step_runs:
                        step_run['steprunid'] = uuid.uuid4()
                        step_run['transactionrunid'] = run['transactionrunid']

                        for field in 'runstart', 'runend':
                            try:
                                extracted_field = self.str_to_datetime(step_run[field])
                                step_run[field] = datetime.strftime(extracted_field, '%Y-%m-%d %H:%M:%S.%f')
                            except Exception:
                                step_run[field] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                    try:
                        extracted_runend = self.str_to_datetime(run['runend'])
                        run['runend'] = datetime.strftime(extracted_runend, '%Y-%m-%d %H:%M:%S.%f')
                    except Exception:
                        run['runend'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                    step_runs.extend(current_step_runs)

                ORM.Transaction_Run.insert_many(runs_data['runs']).execute()
                ORM.Step_Run.insert_many(step_runs).execute()
                return JSONResponse(content={'message': f"Run(s) added successfully!", 'ids': self.json_reserialize(uuids)})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while creating run: {e}'}, status_code=500)
