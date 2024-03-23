import sys
import time
import peewee
from orm.config import config

db = peewee.PostgresqlDatabase('primoart')


class BaseModel(peewee.Model):
    print("Waiting for database to be ready...", file=sys.stderr)
    time.sleep(1)

    @staticmethod
    def extract_data_from_select_dict(dict):
        return dict['__data__']

    class Meta:
        try:
            database = peewee.PostgresqlDatabase(config.db_name,
                                             user=config.db_user,
                                             host=config.db_host,
                                             port=config.db_port,
                                             password=config.db_password)
        except Exception as e:
            raise ConnectionError(f'Error while connecting to Postgres ({config.db_host}:{config.db_port}): {e}')

        schema = config.db_schema
        primary_key = False


class Robots(BaseModel):
    robotid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=1000)
    city = peewee.CharField(max_length=1000)
    lattitude = peewee.FloatField()
    longitude = peewee.FloatField()
    ipaddr = peewee.CharField(max_length=1000)
    createddatetime = peewee.DateTimeField()
    createdby = peewee.CharField(max_length=1000)

    class Meta:
        table_name = 'robots'


class Services(BaseModel):
    serviceid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=1000)
    description = peewee.CharField(max_length=1000)
    createddatetime = peewee.DateTimeField()
    createdby = peewee.CharField(max_length=1000)

    class Meta:
        table_name = 'services'


class Business_Process(BaseModel):
    processid = peewee.UUIDField(primary_key=True, unique=True)
    serviceid = peewee.UUIDField()
    name = peewee.CharField(max_length=1000)
    description = peewee.CharField(max_length=1000)
    createddatetime = peewee.DateTimeField()
    createdby = peewee.CharField(max_length=1000)
    state = peewee.CharField(max_length=1000)

    class Meta:
        table_name = 'business_processes'


class Transaction(BaseModel):
    transactionid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=1000)
    processid = peewee.UUIDField(null=True)
    description = peewee.CharField(max_length=1000)
    createddatetime = peewee.DateTimeField()
    createdby = peewee.CharField(max_length=1000, null=True)
    state = peewee.CharField(max_length=1000, null=True)
    cron = peewee.CharField(max_length=1000, default='not scheduled')

    class Meta:
        table_name = 'transactions'


class Transaction_Run(BaseModel):
    transactionid = peewee.UUIDField()
    transactionrunid = peewee.UUIDField(primary_key=True, unique=True)
    robotid = peewee.CharField(max_length=1000)
    runstart = peewee.DateTimeField()
    runend = peewee.DateTimeField(null=True)
    runresult = peewee.CharField(max_length=1000, null=True)
    logid = peewee.UUIDField(null=True)
    errorcode = peewee.IntegerField(null=True)

    class Meta:
        table_name = 'transactions_runs'


class Step_Info(BaseModel):
    stepid = peewee.UUIDField(primary_key=True, unique=True)
    transactionid = peewee.UUIDField()
    name = peewee.CharField(max_length=1000)
    description = peewee.CharField(max_length=1000)
    createddatetime = peewee.DateTimeField()
    createdby = peewee.CharField(max_length=1000)

    class Meta:
        table_name = 'step_info'


class Step_Run(BaseModel):
    steprunid = peewee.UUIDField()
    stepid = peewee.UUIDField()
    transactionrunid = peewee.UUIDField()
    runstart = peewee.DateTimeField()
    runend = peewee.DateTimeField()
    runresult = peewee.CharField(max_length=1000)
    logid = peewee.UUIDField()
    screenshotid = peewee.UUIDField()
    errorcode = peewee.IntegerField()

    class Meta:
        table_name = 'step_runs'

# auto create schemas and tables
db.create_tables([Transaction, Transaction_Run, Step_Info, Step_Run, Robots, Services, Business_Process])
