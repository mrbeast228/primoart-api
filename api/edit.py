from fastapi import Body
from starlette.responses import JSONResponse

from orm.config import config
if config.db_type == 'clickhouse':
    import orm.clickhouse as ORM
elif config.db_type == 'postgres':
    import orm.postgres as ORM
else:
    raise TypeError(f'Database {config.db_type} not supported!')
from api.core import APICore, app


class PUT(APICore):
    def __init__(self):
        super().__init__()

        @app.put("/robots/{robot_id}")
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


        @app.put("/services/{service_id}")
        async def update_service(service_id: str, service_patch: dict = Body(..., example={"service_patch":
                                                                                              {"name": "TEST PATCH"}
                                                                                        })):
                try:
                 self.validate_uuid4(service_id)

                 # we need to check if service with such ID exists
                 if not ORM.Services.select().where(ORM.Services.serviceid == service_id):
                      return JSONResponse(content={'error': f'Service with ID {service_id} does not exist!'},
                                         status_code=404)

                 if not 'service_patch' in service_patch \
                            or not isinstance(service_patch['service_patch'], dict):
                      return JSONResponse(content={'error': 'Invalid service patch format!'}, status_code=400)

                 ORM.Services.update(**(service_patch['service_patch'])) \
                      .where(ORM.Services.serviceid == service_id).execute()
                 return JSONResponse(content={'message': f"Service {service_id} updated successfully!"})

                except Exception as e:
                 return JSONResponse(content={'error': f'Error while updating service: {e}'}, status_code=500)


        @app.put("/services/{service_id}/business_processes/{process_id}")
        @app.put("/business_processes/{process_id}")
        async def update_business_process(process_id: str, service_id: str = '', process_patch: dict = Body(..., example={"process_patch":
                                                                                                                            {"name": "TEST PATCH"}
                                                                                                                        })):
            try:
                if service_id:
                    self.validate_uuid4(service_id)
                self.validate_uuid4(process_id)

                # we need to check if business process with such ID exists
                if not ORM.Business_Process.select().where(ORM.Business_Process.processid == process_id):
                    return JSONResponse(content={'error': f'Business process with ID {process_id} does not exist!'},
                                        status_code=404)
                if not 'process_patch' in process_patch:
                    return JSONResponse(content={'error': 'Invalid business process format!'}, status_code=400)

                ORM.Business_Process.update(**(process_patch['process_patch'])).where(
                    ORM.Business_Process.processid == process_id).execute()
                return JSONResponse(content={'message': f"Business process {process_id} updated successfully!"})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while updating business process: {e}'}, status_code=500)


        @app.put("/transactions/{transaction_id}")
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


        @app.put("/transactions/{transaction_id}/steps/{step_id}")
        @app.put("/steps/{step_id}")
        async def update_transaction_step(step_id: str, transaction_id: str = '', step_patch: dict = Body(..., example={"step_patch":
                                                                                                                            {"name": "TEST PATCH"}
                                                                                                                        })):
            try:
                if transaction_id:
                    self.validate_uuid4(transaction_id)
                self.validate_uuid4(step_id)

                # we need to check if step with such ID exists
                if not ORM.Step_Info.select().where(ORM.Step_Info.stepid == step_id):
                    return JSONResponse(content={'error': f'Step with ID {step_id} does not exist!'}, status_code=404)
                if not 'step_patch' in step_patch:
                    return JSONResponse(content={'error': 'Invalid step format!'}, status_code=400)

                ORM.Step_Info.update(**(step_patch['step_patch'])).where(
                    ORM.Step_Info.stepid == step_id).execute()
                return JSONResponse(content={'message': f"Step {step_id} updated successfully!"})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while updating step: {e}'}, status_code=500)
