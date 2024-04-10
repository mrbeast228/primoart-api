import datetime

from fastapi import Body
from starlette.responses import JSONResponse

from api.base_read import BaseGET
from api.core import app
from orm import postgres as ORM


class MatrixGET(BaseGET):
    def __init__(self):
        super().__init__()

        @app.get('/runs/heatmap', tags=['Read dynamic data'])
        async def get_runs_heatmap(filter_body: dict = Body({})):
            try:
                now, monday, midnight, start_date, end_date, prev_start =\
                    self.date_logic(filter_body)

                # step 0 - determine filtering type - by process or by service
                process_id = filter_body.pop('processid', None)
                service_id = filter_body.pop('serviceid', None)
                transaction_id = filter_body.pop('transactionid', None)
                if service_id:
                    transactions = ORM.Transaction.select(ORM.Transaction.transactionid)\
                        .where(ORM.Transaction.serviceid == service_id)
                    transaction_ids = [str(transaction.transactionid) for transaction in transactions]
                elif process_id:
                    services = ORM.Service.select(ORM.Service.serviceid)\
                        .where(ORM.Service.processid == process_id)
                    service_ids = [str(service.serviceid) for service in services]
                    transactions = ORM.Transaction.select(ORM.Transaction.transactionid)\
                        .where(ORM.Transaction.serviceid << service_ids)
                    transaction_ids = [str(transaction.transactionid) for transaction in transactions]
                elif transaction_id:
                    transaction_ids = [transaction_id]
                else:
                    raise KeyError('No process ID, service ID or transaction ID provided')


                # step 0.1 - subtract 1 second from end date to solve problems with 00:00:00
                end_date -= datetime.timedelta(seconds=1)

                # step 1 - prepare heatmap array 7x24 with -1 by default
                start_day = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
                heatmap = [[{} for _ in range(24)] for _ in range(7)]
                one_hour_diff = datetime.timedelta(hours=1)

                # step 2 - start filling heatmap with data
                current_hour = start_day - one_hour_diff
                while current_hour < end_date:
                    current_hour += one_hour_diff
                    if current_hour < start_date: # filter may start not from midnight
                        continue
                    run_data = self.get_runs_for_list(transaction_ids, current_hour, current_hour + one_hour_diff)
                    heatmap[current_hour.weekday()][current_hour.hour] = run_data # kepp all data for range

                return JSONResponse(content={'heatmap': heatmap})

            except Exception as e:
                return JSONResponse(content={'error': f'Error while getting heatmap: {e}'}, status_code=500)