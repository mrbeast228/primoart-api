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
	fake_robot_list = []
	fake_service_list = []
	fake_business_process_list = []
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

	def genNewRobots(self, cnt=4):
		self.fake_robot_list.extend([mvp.FakeRobot().__dict__ for i in range(cnt)])
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/robots'
			response = requests.post(url, json={"robots": APICore.json_reserialize(self.fake_robot_list)})
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')

		except Exception as e:
			print(f'Error while inserting robots: {e}')
			exit(1)

	def getExistingRobots(self):
		self.fake_robot_list.clear()
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/robots'
			response = requests.get(url)
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			self.fake_robot_list.extend(response.json()['robots'])

		except Exception as e:
			print(f'Error while getting robots: {e}')
			exit(1)

	def workOnRobots(self):
		self.getExistingRobots()
		if not self.fake_robot_list:
			self.genNewRobots()

	def genNewServices(self, cnt=10):
		self.fake_service_list.extend([mvp.FakeService().__dict__ for i in range(random.randint(cnt // 2, cnt))])
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/services'
			response = requests.post(url, json={"services": APICore.json_reserialize(self.fake_service_list)})
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')

		except Exception as e:
			print(f'Error while inserting services: {e}')
			exit(1)

	def getExistingServices(self):
		self.fake_service_list.clear()
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/services'
			response = requests.get(url)
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			self.fake_service_list.extend(response.json()['services'])

		except Exception as e:
			print(f'Error while getting services: {e}')
			exit(1)

	def workOnServices(self):
		self.getExistingServices()
		if not self.fake_service_list:
			self.genNewServices()

	def genNewBusinessProcesses(self, cnt=5):
		# drop previous business processes list
		self.fake_business_process_list.clear()

		# Для каждой услуги делаем от 1 до 3 бизнес-процессов (рандомно)
		for fake_service in self.fake_service_list:
			try:
				busines_processes = [mvp.FakeBusinessProcess(fake_service['serviceid']).__dict__
									 for i in range(random.randint(cnt // 2, cnt))]
				self.fake_business_process_list.extend(busines_processes)

				url = f'http://{config.api_endpoint}:{config.api_port}/services/{fake_service["serviceid"]}/business_processes'
				response = requests.post(url, json={"business_processes": APICore.json_reserialize(busines_processes)})
				if response.status_code != 200:
					raise ConnectionError(f'API Error: {response.status_code} {response.text}')

			except Exception as e:
				print(f'Error while inserting business processes: {e}')
				exit(1)

	def getExistingBusinessProcesses(self):
		# drop previous business processes list
		self.fake_business_process_list.clear()

		# extend it by list of existing business processes
		try:
			url = f'http://{config.api_endpoint}:{config.api_port}/business_processes'
			response = requests.get(url)
			if response.status_code != 200:
				raise ConnectionError(f'API Error: {response.status_code} {response.text}')
			self.fake_business_process_list.extend(response.json()['business_processes'])

		except Exception as e:
			print(f'Error while getting business processes: {e}')
			exit(1)

	def workOnBusinessProcesses(self):
		self.getExistingBusinessProcesses()
		if not self.fake_business_process_list:
			self.genNewBusinessProcesses()

	def genNewTrans(self, cnt=10):
		# drop previous transactions list
		self.fake_transaction_list.clear()

		# Для каждого бизнес-процесса делаем от 1 до 10 транзакций (рандомно)
		for fake_business_process in self.fake_business_process_list:
			try:
				transactions = [mvp.FakeTransaction(fake_business_process['processid']).__dict__
								for i in range(random.randint(cnt // 2, cnt))]
				self.fake_transaction_list.extend(transactions)

				url = f'http://{config.api_endpoint}:{config.api_port}/business_processes/{fake_business_process["processid"]}/transactions'
				response = requests.post(url, json={"transactions": APICore.json_reserialize(transactions)})
				if response.status_code != 200:
					raise ConnectionError(f'API Error: {response.status_code} {response.text}')

			except Exception as e:
				print(f'Error while inserting transactions: {e}')
				exit(1)

	def getExistingTrans(self):
		# drop previous transactions list
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

	def genNewTransSteps(self, cnt=10):
		# drop previous trans steps list
		self.fake_transaction_step_list.clear()

		# Для каждой транзакции делаем от 5 до 10 шагов (рандомно)
		for fake_transaction in self.fake_transaction_list:
			try:
				steps = [mvp.FakeStepInfo(fake_transaction['transactionid'], fake_transaction['createdby']).__dict__
						 for i in range(random.randint(cnt // 2, cnt))]
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
				robot = random.choice(self.fake_robot_list)
				fake_transaction_run = mvp.FakeTransactionRun(fake_transaction['transactionid'], robot['robotid']).__dict__
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
	filler.workOnRobots()
	filler.workOnServices()
	filler.workOnBusinessProcesses()
	filler.workOnTrans()
	filler.workOnTransSteps()
	filler.doRuns()

if __name__ == '__main__':
	main()
