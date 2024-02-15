import uuid
import requests
import wonderwords
import datetime
import random

from api.core import APICore
from orm.config import config

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
	fake_transaction_list = []
	fake_transaction_step_list = []

	def genNewTrans(self, cnt=10):
		# drop previous trans list
		self.fake_transaction_list.clear()

		# Делаем 10 транзакций
		self.fake_transaction_list.extend([FakeTransaction().__dict__ for i in range(cnt)])

		# insert them into db
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/transactions'
			data = {"transactions": self.fake_transaction_list}
			response = requests.post(url, json=APICore.json_reserialize(data))
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')

		except Exception as e:
			print(f'Error while adding transactions: {e}')
			exit(1)

	def getExistingTrans(self):
		# drop previous trans list
		self.fake_transaction_list.clear()

		# extend it by list of existing transactions
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/transactions'
			response = requests.get(url)
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			self.fake_transaction_list.extend(response.json()['transactions'])

		except Exception as e:
			print(f'Error while getting transactions: {e}')
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
			try:
				steps = [FakeStepInfo(fake_transaction['transactionid'], fake_transaction['createdby']).__dict__
					 	for i in range(random.randint(5, 10))]
				self.fake_transaction_step_list.extend(steps)

				url = f'http://{config.api_endpoint}:{config.api_port}/transactions/{fake_transaction["transactionid"]}/steps'
				response = requests.post(url, json={"steps": APICore.json_reserialize(steps)})
				if response.status_code != 200:
					raise ConnectionError(f'API Error: {response.status_code} {response.text}')

			except Exception as e:
				print(f'Error while adding steps: {e}')
				exit(1)

	def getExistingTransSteps(self):
		# drop previous trans steps list
		self.fake_transaction_step_list.clear()

		# extend it by list of existing transactions steps
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/steps'
			response = requests.get(url)
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			self.fake_transaction_step_list.extend(response.json()['steps'])

		except Exception as e:
			print(f'Error while getting steps: {e}')
			exit(1)

	def workOnTransSteps(self):
		self.getExistingTransSteps()
		if not self.fake_transaction_step_list:
			self.genNewTransSteps()

	def doRuns(self):
		# Для каждой транзакции делаем по 10-20 запусков
		for fake_transaction in self.fake_transaction_list:
			runs = []
			for i in range(random.randint(10, 20)):
				fake_transaction_run = FakeTransactionRun(fake_transaction['transactionid']).__dict__
				fake_transaction_run['step_runs'] = []

				# И для каждого запуска транзакции заполняем его шаги
				fake_transaction_run["runresult"] = "OK"
				for fake_transaction_step in self.fake_transaction_step_list:
					if fake_transaction_step['transactionid'] == fake_transaction['transactionid']:
						fake_transaction_step_run = FakeStepRun(fake_transaction_run['transactionrunid'],
																fake_transaction_step['stepid']).__dict__
						fake_transaction_run['step_runs'].append(fake_transaction_step_run)
						if fake_transaction_step_run['runresult'] != "OK": # logical and
							fake_transaction_run["runresult"] = fake_transaction_step_run['runresult']

				runs.append(fake_transaction_run)

			try:
				url = f'http://{config.api_endpoint}:{config.api_port}/transactions/{fake_transaction["transactionid"]}/runs'
				response = requests.post(url, json={"runs": APICore.json_reserialize(runs)})
				if response.status_code != 200:
					raise ConnectionError(f'API Error: {response.status_code} {response.text}')

			except Exception as e:
				print(f'Error while inserting runs: {e}')
				exit(1)


def main():
	# gen only new runs for existing transactions and steps by default
	filler = Filler()
	filler.workOnTrans()
	filler.workOnTransSteps()
	filler.doRuns()


if __name__ == '__main__':
	main()
