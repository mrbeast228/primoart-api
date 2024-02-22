import sys
import time
import infi.clickhouse_orm as click
from orm.config import config


# here BaseModel not only model but also compatibility layer with the most used peewee methods
class BaseModel(click.Model):
    print("Waiting for database to be ready...", file=sys.stderr)
    time.sleep(3) # clickhouse is slower to start

    try:
        _database = click.Database(config.db_name,
                               db_url=f'http://{config.db_host}:{config.db_port}',
                               username=config.db_user,
                               password=config.db_password,
                               verify_ssl_cert=False)
    except Exception as e:
        raise ConnectionError(f'Error while connecting to Clickhouse (http://{config.db_host}:{config.db_port}): {e}')

    # peewee-compatibility aliases
    @staticmethod
    def create_tables(tables, **kwargs):
        # kwargs ignored - creating is always safe
        for table in tables:
            BaseModel._database.create_table(table)

    _database.create_tables = create_tables.__get__(_database)
    click.CharField = click.StringField
    click.QuerySet.where = click.QuerySet.filter

    # query subclass to make possible do raw queries
    class SQLQuery:
        _query = None
        _keys = []

        def __init__(self, query, keys=None):
            self._query = query
            if isinstance(keys, list):
                self._keys.extend(keys)

        def where(self, *args):
            # work with F values
            self._query += ' WHERE ' + ' AND '.join([f'{arg.args[0]} = \'{arg.args[1]}\'' for arg in args])
            return self

        def execute(self):
            raw_output = BaseModel._database.raw(self._query)
            row_list = raw_output.split('\n')
            result = []
            for row in row_list:
                subres = {}
                col_list = row.split('\t')
                for i in range(len(self._keys)):
                    subres[self._keys[i]] = col_list[i]
                result.append(subres)
            return result

        def __iter__(self):
            return self.execute()

    @staticmethod
    def extract_data_from_select_dict(dict):
        result = dict.copy()
        result.pop('_database')
        return result

    @classmethod
    def create_table(cls):
        cls._database.create_table(cls)

    @classmethod
    def drop_table(cls):
        cls._database.drop_table(cls)

    @classmethod
    def bulk_create(cls, list_of_models):
        cls._database.insert(list_of_models)

    @classmethod
    def insert_many(cls, list_of_dicts):
        cls._database.insert([cls(**d) for d in list_of_dicts])
        return cls

    @classmethod
    def select(cls, *args):
        select_base = cls.objects_in(cls._database)
        return select_base if not args else select_base.only(*args)

    # works as select - where - delete
    @classmethod
    def delete(cls, *args):
        cls.select().where(*args).delete()
    @classmethod
    def create(cls, **kwargs):
        cls._database.insert([kwargs])
        return cls

    @classmethod
    def update(cls, **kwargs):
        # need to write raw ALTER TABLE query
        update_values = ', '.join([f'{k} = \'{v}\'' for k, v in kwargs.items()])
        return cls.SQLQuery(f'ALTER TABLE {cls.table_name()} UPDATE {update_values}', kwargs.keys())

    @classmethod
    def bulk_update(cls, *args, **kwargs):
        raise NotImplementedError('Bulk update is not supported by Clickhouse')

    # actually do nothing for clickhouse
    @classmethod
    def execute(cls):
        pass

# keeping connection with Postgres requires db to be globally declared, keep compatibility
db = BaseModel._database


class Transaction(BaseModel):
    transactionid = click.UUIDField()
    name = click.StringField()
    serviceid = click.NullableField(click.UUIDField())
    robotid = click.StringField()
    description = click.StringField()
    createddatetime = click.DateTime64Field(precision=6)
    createdby = click.NullableField(click.StringField())
    state = click.NullableField(click.StringField())
    cron = click.StringField(default='not scheduled')

    engine = click.MergeTree('createddatetime', ('transactionid',))

    @classmethod
    def table_name(cls):
        return 'transactions'


class Transaction_Run(BaseModel):
    transactionid = click.UUIDField()
    transactionrunid = click.UUIDField()
    runstart = click.DateTime64Field(precision=6)
    runend = click.DateTime64Field(precision=6)
    runresult = click.StringField()
    logid = click.NullableField(click.UUIDField())
    errorcode = click.NullableField(click.Int32Field())

    engine = click.MergeTree(order_by=('transactionid', 'runend'), partition_key=('transactionid',))

    @classmethod
    def table_name(cls):
        return 'transactions_runs'


class Step_Info(BaseModel):
    stepid = click.UUIDField()
    transactionid = click.UUIDField()
    name = click.StringField()
    description = click.StringField()
    createddatetime = click.DateTime64Field(precision=6)
    createdby = click.StringField()

    engine = click.MergeTree('createddatetime', ('stepid',))

    @classmethod
    def table_name(cls):
        return 'step_info'


class Step_Run(BaseModel):
    steprunid = click.UUIDField()
    stepid = click.UUIDField()
    transactionrunid = click.UUIDField()
    runstart = click.DateTime64Field(precision=6)
    runend = click.DateTime64Field(precision=6)
    runresult = click.StringField()
    logid = click.UUIDField()
    screenshotid = click.UUIDField()
    errorcode = click.Int32Field()

    engine = click.MergeTree(order_by=('stepid', 'transactionrunid', 'runend'), partition_key=('stepid',))

    @classmethod
    def table_name(cls):
        return 'step_runs'

# auto create tables
BaseModel.create_tables([Transaction, Transaction_Run, Step_Info, Step_Run])
