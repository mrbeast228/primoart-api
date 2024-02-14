import uuid
import time
import wonderwords
import datetime
import random

from orm.config import config
if config.db_type == 'clickhouse':
	import orm.clickhouse as ORM
elif config.db_type == 'postgres':
	import orm.postgres as ORM
else:
	raise TypeError(f'Database {config.db_type} not supported!')


# generate dummy data
class FakeTransaction():
	def __init__(self):
		self.transactionid = uuid.uuid4()
		self.name = f"tr-{self.get_random_word()}-{self.get_random_word()}"
		self.robotid = self.get_robot()
		self.description = f"An awesome transaction {self.name} executed by robot {self.robotid}"
		self.createddatetime = datetime.datetime.now()
		self.createdby = self.get_creator()
		self.state = random.choice(['ACTIVE'] * 5 + ['INACTIVE'])

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_robot(self):
		return 'robot-' + random.choice(["astra", "windows", "centos"])

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeTransactionRun():
	def __init__(self, transactionid):
		self.transactionid = transactionid
		self.transactionrunid = uuid.uuid4()
		self.runstart = datetime.datetime.now()
		self.runend = datetime.datetime.now() + datetime.timedelta(milliseconds=random.randint(100, 800))

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_robot(self):
		return 'robot-' + random.choice(["astra", "windows", "centos"])

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeStepInfo():
	def __init__(self, transactionid, creator):
		self.stepid = uuid.uuid4()
		self.transactionid = transactionid
		self.name = f"step-{self.get_random_word()}"
		self.description = f"An step to do {self.get_random_word()} and {self.get_random_word()}"
		self.createddatetime = datetime.datetime.now()
		self.createdby = creator

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()


class FakeStepRun():
	def __init__(self, transactionrunid, stepid):
		self.steprunid = uuid.uuid4()
		self.stepid = stepid
		self.transactionrunid = transactionrunid
		self.runstart = datetime.datetime.now()
		self.runend = datetime.datetime.now() + datetime.timedelta(milliseconds=random.randint(50, 300))
		self.runresult = self.get_run_result()
		self.logid = uuid.uuid4()
		self.screencaptureid = uuid.uuid4()
		self.errorcode = self.get_error_code(self.runresult)

	def get_run_result(self):
		result = ["OK" for i in range(22)]
		result.extend(["WARNING", "FAIL"])
		return random.choice(result)

	def get_error_code(self, runresult):
		error_codes = {"OK": 0, "WARNING": 1, "FAIL": 2}
		return error_codes[runresult]


# main filter class
class Filler:
	# list of tables to be fulfilled by dummy data
	tables = [ORM.Step_Info,
			  ORM.Step_Run,
			  ORM.Transaction,
			  ORM.Transaction_Run]
	fake_transaction_list = []
	fake_transaction_step_list = []

	def regenTables(self):
		try:
			ORM.db.create_tables(self.tables, safe=True)
		except Exception as e:
			print(f'Error while creating tables: {e}')
			exit(1)

	def genNewTrans(self, cnt=10):
		# drop previous trans list
		self.fake_transaction_list.clear()

		# Делаем 10 транзакций
		for i in range(cnt):
			self.fake_transaction_list.append(FakeTransaction().__dict__)

		# insert them into db
		try:
			start_time = time.time()
			ORM.Transaction.insert_many(self.fake_transaction_list).execute()
			print(f'Inserting 10 transactions taken {time.time() - start_time} seconds')
		except Exception as e:
			print(f'Error while inserting transactions: {e}')
			exit(1)

	def getExistingTrans(self):
		# drop previous trans list
		self.fake_transaction_list.clear()

		# extend it by list of existing transactions
		try:
			self.fake_transaction_list.extend([ORM.BaseModel.extract_data_from_select_dict(transaction.__dict__)
											   for transaction in ORM.Transaction.select()])
		except Exception as e:
			print(f'Error while selecting transactions: {e}')
			exit(1)

	def workOnTrans(self):
		self.getExistingTrans()
		if not self.fake_transaction_list:
			self.genNewTrans()

	def genNewTransSteps(self):
		# drop previous trans steps list
		self.fake_transaction_step_list.clear()

		# Для каждой транзакции делаем от 5 до 10 шагов (рандомно)
		for fake_transaction in self.fake_transaction_list:
			for i in range(random.randint(5, 10)):
				self.fake_transaction_step_list.append(FakeStepInfo(fake_transaction['transactionid'], fake_transaction['createdby']).__dict__)

		# insert them into db
		try:
			ORM.Step_Info.insert_many(self.fake_transaction_step_list).execute()
		except Exception as e:
			print(f'Error while inserting steps: {e}')
			exit(1)

	def getExistingTransSteps(self):
		# drop previous trans steps list
		self.fake_transaction_step_list.clear()

		# extend it by list of existing transactions steps
		try:
			self.fake_transaction_step_list.extend([ORM.BaseModel.extract_data_from_select_dict(transaction_step.__dict__)
													for transaction_step in ORM.Step_Info.select()])
		except Exception as e:
			print(f'Error while selecting steps: {e}')
			exit(1)

	def workOnTransSteps(self):
		self.getExistingTransSteps()
		if not self.fake_transaction_step_list:
			self.genNewTransSteps()

	def doRuns(self):
		# Для каждой транзакции делаем по 10-20 запусков
		update_counter = 0
		runs = []
		step_runs = []
		for fake_transaction in self.fake_transaction_list:
			for i in range(random.randint(10, 20)):
				fake_transaction_run = FakeTransactionRun(fake_transaction['transactionid']).__dict__

				# И для каждого запуска транзакции заполняем его шаги
				result = "OK"
				for fake_transaction_step in self.fake_transaction_step_list:
					if fake_transaction_step['transactionid'] == fake_transaction['transactionid']:
						fake_transaction_step_run = FakeStepRun(fake_transaction_run['transactionrunid'],
																fake_transaction_step['stepid']).__dict__
						step_runs.append(fake_transaction_step_run)

						# HOOK: update lastruntime and lastrunresult in current transaction
						try:
							ORM.Step_Info.update(
												lastruntime=fake_transaction_step_run['runend'],
												lastrunresult=fake_transaction_step_run['runresult'])\
								.where(ORM.Step_Info.stepid == fake_transaction_step['stepid'])\
								.execute()
						except Exception as e:
							print(f'Error while updating step info: {e}')
							exit(1)
						update_counter += 1

						if fake_transaction_step_run['runresult'] == "FAIL":
							result = "FAIL"

				# На основе рузельтатов всех шагов записываем результата транзакции
				fake_transaction_run['runresult'] = result

				# HOOK: update lastruntime and lastrunresult in current transaction
				try:
					ORM.Transaction.update(lastruntime=fake_transaction_run['runend'],
																 lastrunresult=result)\
						.where(ORM.Transaction.transactionid == fake_transaction['transactionid'])\
						.execute()
				except Exception as e:
					print(f'Error while updating transaction info: {e}')
					exit(1)
				update_counter += 1

				runs.append(fake_transaction_run)

		# insert them into db
		try:
			ORM.Transaction_Run.insert_many(runs).execute()
		except Exception as e:
			print(f'Error while inserting transaction runs: {e}')
			exit(1)

		try:
			ORM.Step_Run.insert_many(step_runs).execute()
		except Exception as e:
			print(f'Error while inserting step runs: {e}')
			exit(1)

		print("DEBUG: update_counter =", update_counter)


def main():
	# gen only new runs for existing transactions and steps by default
	start_time = time.time()
	filler = Filler()
	filler.regenTables()
	filler.workOnTrans()
	filler.workOnTransSteps()
	filler.doRuns()
	print(f'Generating taken {time.time() - start_time} seconds')


if __name__ == '__main__':
	main()
