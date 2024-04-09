import datetime

from peewee import fn, SQL

from api.core import APICore
from orm import postgres as ORM


class BaseGET(APICore):
    def __init__(self):
        super().__init__()

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
