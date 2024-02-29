import os
import uuid
import requests
import datetime
import random
from pathlib import Path

import mvp.fake_classes as mvp
from api.core import APICore
from orm.config import config

class Filler:
	fake_transaction_list = []
	fake_transaction_step_list = []
	current_logs = []

	@staticmethod
	def genScreenshot(status):
		path = (Path(__file__).parent / 'assets' / 'screenshots' / status).resolve()
		file = open(path / random.choice(os.listdir(path)), 'rb')

		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/screenshots'
			files = {'file': file}
			response = requests.post(url, files=files)
			file.close()
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			return response.json()['screenshot_id']

		except Exception as e:
			print(f'Error while adding screenshot: {e}')
			exit(1)

	def genLog(self):
		log = '\n'.join(
			[f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}]'
			 f'{mvp.fake.sentence(nb_words=10, variable_nb_words=True)}'
			for i in range(random.randint(20, 50))]
		)
		bytes = log.encode('utf-8')
		self.current_logs.append(log)

		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/logs'
			response = requests.post(url, files={'file': bytes})
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			return response.json()['log_id']

		except Exception as e:
			print(f'Error while adding log: {e}')
			exit(1)

	def concatLogs(self):
		result_log = '\n\n'.join(self.current_logs)
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/logs'
			response = requests.post(url, files={'file': result_log.encode('utf-8')})
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')

			self.current_logs.clear()
			return response.json()['log_id']

		except Exception as e:
			print(f'Error while adding log: {e}')
			exit(1)

	def genNewTrans(self, cnt=10):
		# drop previous trans list
		self.fake_transaction_list.clear()

		# Делаем 10 транзакций
		self.fake_transaction_list.extend([mvp.FakeTransaction().__dict__ for i in range(cnt)])

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
				steps = [mvp.FakeStepInfo(fake_transaction['transactionid'], fake_transaction['createdby']).__dict__
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
			for i in range(random.randint(config.mvp_min_runs, config.mvp_min_runs * 2)):
				fake_transaction_run = mvp.FakeTransactionRun(fake_transaction['transactionid']).__dict__
				fake_transaction_run['step_runs'] = []

				# И для каждого запуска транзакции заполняем его шаги
				fake_transaction_run["runresult"] = "OK"
				for fake_transaction_step in self.fake_transaction_step_list:
					if fake_transaction_step['transactionid'] == fake_transaction['transactionid']:
						fake_transaction_step_run = mvp.FakeStepRun(fake_transaction_run['transactionrunid'],
																fake_transaction_step['stepid']).__dict__

						# logs and screenshots
						fake_transaction_step_run['logid'] = self.genLog() if config.mvp_create_artifacts else str(uuid.uuid4())
						fake_transaction_step_run['screenshotid'] = self.genScreenshot(fake_transaction_step_run['runresult']) if config.mvp_create_artifacts else str(uuid.uuid4())

						fake_transaction_run['step_runs'].append(fake_transaction_step_run)
						if fake_transaction_step_run['runresult'] != "OK": # logical and
							fake_transaction_run["runresult"] = fake_transaction_step_run['runresult']

				# work on logs todo
				fake_transaction_run['logid'] = self.concatLogs() if config.mvp_create_artifacts else str(uuid.uuid4())
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
