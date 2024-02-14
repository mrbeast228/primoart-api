import peewee
from orm.config import config

db = peewee.PostgresqlDatabase('primoart')


class BaseModel(peewee.Model):
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


class Transaction(BaseModel):
	transactionid = peewee.UUIDField(primary_key=True, unique=True)
	name = peewee.CharField(max_length=1000)
	robotid = peewee.CharField(max_length=1000)
	description = peewee.CharField(max_length=1000)
	createddatetime = peewee.DateTimeField()
	createdby = peewee.CharField(max_length=1000, null=True)
	state = peewee.CharField(max_length=1000, null=True)
	lastruntime = peewee.DateTimeField(null=True)
	lastrunresult = peewee.CharField(max_length=1000, null=True)

	class Meta:
		table_name = 'transactions'


class Transaction_Run(BaseModel):
	transactionid = peewee.UUIDField()
	transactionrunid = peewee.UUIDField(primary_key=True, unique=True)
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
	lastruntime = peewee.DateTimeField(null=True)
	lastrunresult = peewee.CharField(max_length=1000, null=True)

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
	screencaptureid = peewee.UUIDField()
	errorcode = peewee.IntegerField()

	class Meta:
		table_name = 'step_runs'
