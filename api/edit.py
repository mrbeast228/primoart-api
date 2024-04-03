from fastapi import Body
from starlette.responses import JSONResponse

import orm.postgres as ORM # only postgres is supported now

from api.core import APICore, app


class PUT(APICore):
    def __init__(self):
        super().__init__()

        @app.put("/robots/{robot_id}", tags=['Edit data'])
        async def update_robot(robot_id: str, robot_patch: dict = Body(..., example={"robot_patch":
                                                                                        {"name": "TEST PATCH"}
                                                                                                         })):
                try:
                 self.validate_uuid4(robot_id)

                 # we need to check if robot with such ID exists
                 if not ORM.Robots.select().where(ORM.Robots.robotid == robot_id):
                      return JSONResponse(content={'error': f'Robot with ID {robot_id} does not exist!'},
                                         status_code=404)

                 if not 'robot_patch' in robot_patch \
                            or not isinstance(robot_patch['robot_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid robot patch format!'}, status_code=400)

                 ORM.Robots.update(**(robot_patch['robot_patch'])) \
                      .where(ORM.Robots.robotid == robot_id).execute()
                 return JSONResponse(content={'message': f"Robot {robot_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating robot: {e}'}, status_code=500)

        @app.put("/processes/{process_id}", tags=['Edit data'])
        async def update_process(process_id: str, process_patch: dict = Body(..., example={"process_patch":
                                                                                            {"name": "TEST PATCH"}
                                                                                                             })):
                try:
                 self.validate_uuid4(process_id)

                 # we need to check if process with such ID exists
                 if not ORM.Process.select().where(ORM.Process.processid == process_id):
                      return JSONResponse(content={'error': f'Process with ID {process_id} does not exist!'},
                                         status_code=404)

                 if not 'process_patch' in process_patch \
                            or not isinstance(process_patch['process_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid process patch format!'}, status_code=400)

                 ORM.Process.update(**(process_patch['process_patch'])) \
                      .where(ORM.Process.processid == process_id).execute()
                 return JSONResponse(content={'message': f"Process {process_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating process: {e}'}, status_code=500)

        @app.put("/services/{service_id}", tags=['Edit data'])
        async def update_service(service_id: str, service_patch: dict = Body(..., example={"service_patch":
                                                                                            {"name": "TEST PATCH"}
                                                                                                             })):
                try:
                 self.validate_uuid4(service_id)

                 # we need to check if service with such ID exists
                 if not ORM.Service.select().where(ORM.Service.serviceid == service_id):
                      return JSONResponse(content={'error': f'Service with ID {service_id} does not exist!'},
                                         status_code=404)

                 if not 'service_patch' in service_patch \
                            or not isinstance(service_patch['service_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid service patch format!'}, status_code=400)

                 ORM.Service.update(**(service_patch['service_patch'])) \
                      .where(ORM.Service.serviceid == service_id).execute()
                 return JSONResponse(content={'message': f"Service {service_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating service: {e}'}, status_code=500)

        @app.put("/transactions/{transaction_id}", tags=['Edit data'])
        async def update_transaction(transaction_id: str, transaction_patch: dict = Body(..., example={"transaction_patch":
                                                                                            {"name": "TEST PATCH"}
                                                                                                             })):
                try:
                 self.validate_uuid4(transaction_id)

                 # we need to check if transaction with such ID exists
                 if not ORM.Transaction.select().where(ORM.Transaction.transactionid == transaction_id):
                      return JSONResponse(content={'error': f'Transaction with ID {transaction_id} does not exist!'},
                                         status_code=404)

                 if not 'transaction_patch' in transaction_patch \
                            or not isinstance(transaction_patch['transaction_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid transaction patch format!'}, status_code=400)

                 ORM.Transaction.update(**(transaction_patch['transaction_patch'])) \
                      .where(ORM.Transaction.transactionid == transaction_id).execute()
                 return JSONResponse(content={'message': f"Transaction {transaction_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating transaction: {e}'}, status_code=500)

        @app.put("/steps/<step_id>", tags=['Edit data'])
        async def update_step(step_id: str, step_patch: dict = Body(..., example={"step_patch":
                                                                                            {"name": "TEST PATCH"}
                                                                                                             })):
                try:
                 self.validate_uuid4(step_id)

                 # we need to check if step with such ID exists
                 if not ORM.Step_Info.select().where(ORM.Step_Info.stepid == step_id):
                      return JSONResponse(content={'error': f'Step with ID {step_id} does not exist!'},
                                         status_code=404)

                 if not 'step_patch' in step_patch \
                            or not isinstance(step_patch['step_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid step patch format!'}, status_code=400)

                 ORM.Step_Info.update(**(step_patch['step_patch'])) \
                      .where(ORM.Step_Info.stepid == step_id).execute()
                 return JSONResponse(content={'message': f"Step {step_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating step: {e}'}, status_code=500)

        @app.put("/runs/<run_id>", tags=['Edit data'])
        async def update_run(run_id: str, run_patch: dict = Body(..., example={"run_patch":
                                                                                            {"name": "TEST PATCH"}
                                                                                                             })):
                try:
                 self.validate_uuid4(run_id)

                 # we need to check if run with such ID exists
                 if not ORM.Transaction_Run.select().where(ORM.Transaction_Run.transactionrunid == run_id):
                      return JSONResponse(content={'error': f'Run with ID {run_id} does not exist!'},
                                         status_code=404)

                 if not 'run_patch' in run_patch \
                            or not isinstance(run_patch['run_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid run patch format!'}, status_code=400)

                 ORM.Transaction_Run.update(**(run_patch['run_patch'])) \
                      .where(ORM.Transaction_Run.transactionrunid == run_id).execute()
                 return JSONResponse(content={'message': f"Run {run_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating run: {e}'}, status_code=500)

        @app.put("/step_runs/<step_run_id>", tags=['Edit data'])
        async def update_step_run(step_run_id: str, step_run_patch: dict = Body(..., example={"step_run_patch":
                                                                                            {"name": "TEST PATCH"}
                                                                                                             })):
                try:
                 self.validate_uuid4(step_run_id)

                 # we need to check if step run with such ID exists
                 if not ORM.Step_Run.select().where(ORM.Step_Run.steprunid == step_run_id):
                      return JSONResponse(content={'error': f'Step run with ID {step_run_id} does not exist!'},
                                         status_code=404)

                 if not 'step_run_patch' in step_run_patch \
                            or not isinstance(step_run_patch['step_run_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid step run patch format!'}, status_code=400)

                 ORM.Step_Run.update(**(step_run_patch['step_run_patch'])) \
                      .where(ORM.Step_Run.steprunid == step_run_id).execute()
                 return JSONResponse(content={'message': f"Step run {step_run_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating step run: {e}'}, status_code=500)
