from starlette.responses import JSONResponse

import orm.postgres as ORM # for now only Postgres is supported

from api.core import APICore, app


class DELETE(APICore):
    def __init__(self):
        super().__init__()

        @app.delete("/robots/{robot_id}", tags=['Remove data'])
        async def delete_robot(robot_id: str):
            try:
                self.validate_uuid4(robot_id)
                ORM.Robots.delete().where(ORM.Robots.robotid == robot_id).execute()
                return JSONResponse(content={'message': f'Robot {robot_id} deleted successfully!'})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while deleting robot {robot_id}: {e}'}, status_code=500)

        @app.delete("/processes/{process_id}", tags=['Remove data'])
        async def delete_process(process_id: str):
            try:
                self.validate_uuid4(process_id)
                ORM.Process.delete().where(ORM.Process.processid == process_id).execute()
                return JSONResponse(content={'message': f'Process {process_id} deleted successfully!'})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while deleting process {process_id}: {e}'}, status_code=500)

        @app.delete("/services/{service_id}", tags=['Remove data'])
        async def delete_service(service_id: str):
            try:
                self.validate_uuid4(service_id)
                ORM.Service.delete().where(ORM.Service.serviceid == service_id).execute()
                return JSONResponse(content={'message': f'Service {service_id} deleted successfully!'})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while deleting service {service_id}: {e}'}, status_code=500)

        @app.delete("/transactions/{transaction_id}", tags=['Remove data'])
        async def delete_transaction(transaction_id: str):
            try:
                self.validate_uuid4(transaction_id)
                ORM.Transaction.delete().where(ORM.Transaction.transactionid == transaction_id).execute()
                return JSONResponse(content={'message': f'Transaction {transaction_id} deleted successfully!'})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while deleting transaction {transaction_id}: {e}'}, status_code=500)

        @app.delete("/steps/{step_id}", tags=['Remove data'])
        async def delete_step(step_id: str):
            try:
                self.validate_uuid4(step_id)
                ORM.Step_Info.delete().where(ORM.Step_Info.stepid == step_id).execute()
                return JSONResponse(content={'message': f'Step {step_id} deleted successfully!'})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while deleting step {step_id}: {e}'}, status_code=500)

        @app.delete("/runs/{run_id}", tags=['Remove data'])
        async def delete_run(run_id: str):
            try:
                self.validate_uuid4(run_id)
                ORM.Transaction_Run.delete().where(ORM.Transaction_Run.transactionrunid == run_id).execute()
                return JSONResponse(content={'message': f'Run {run_id} deleted successfully!'})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while deleting run {run_id}: {e}'}, status_code=500)
