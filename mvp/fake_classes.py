import datetime
import random
import wonderwords

from faker import Faker
fake = Faker()


class FakeRobot():
	def __init__(self):
		self.name = f"robot-{self.get_random_word()}"
		self.city = f"city-{self.get_random_word()}"
		self.latitude = random.uniform(-90, 90)
		self.longitude = random.uniform(-180, 180)
		self.ipaddr = fake.ipv4()
		self.createddatetime = fake.date_time_this_year()
		self.createdby = self.get_creator()

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeProcess():
	def __init__(self):
		self.name = f"process-{self.get_random_word()}"
		self.description = f"An awesome process {self.name}"
		self.createddatetime = fake.date_time_this_year()
		self.createdby = self.get_creator()

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeService():
	def __init__(self, processid):
		self.processid = processid
		self.name = f"service-{self.get_random_word()}"
		self.description = f"An awesome service {self.name}"
		self.createddatetime = fake.date_time_this_year()
		self.createdby = self.get_creator()
		self.state = random.choice(['ACTIVE'] * 5 + ['INACTIVE'])

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeTransaction():
	def __init__(self, serviceid):
		self.name = f"tr-{self.get_random_word()}-{self.get_random_word()}"
		self.serviceid = serviceid
		self.description = f"An awesome transaction {self.name}"
		self.createddatetime = fake.date_time_this_year()
		self.createdby = self.get_creator()
		self.state = random.choice(['ACTIVE'] * 5 + ['INACTIVE'])

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeTransactionRun():
	def __init__(self, transactionid, robotid):
		self.transactionid = transactionid
		self.robotid = robotid
		self.runstart = fake.date_time_this_year()
		self.runend = self.runstart + datetime.timedelta(milliseconds=random.randint(15000, 40000))
		self.log = "BASE64 ENCODED STRING"
		self.screenshot = "BASE64 ENCODED STRING"

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()


class FakeStepInfo():
	def __init__(self, transactionid):
		self.transactionid = transactionid
		self.name = f"step-{self.get_random_word()}"
		self.description = f"An step to do {self.get_random_word()} and {self.get_random_word()}"
		self.createddatetime = fake.date_time_this_year()
		self.createdby = self.get_creator()

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeStepRun():
	def __init__(self, stepid):
		self.stepid = stepid
		self.runstart = fake.date_time_this_year()
		self.runend = self.runstart + datetime.timedelta(milliseconds=random.randint(2000, 9000))
		self.runresult = self.get_run_result()
		self.errorcode = self.get_error_code(self.runresult)

	def get_run_result(self):
		result = ["OK", "WARNING", "FAIL"]
		probabilities = (350, 1, 1)
		return random.choices(result, weights=probabilities, k=1)[0]

	def get_error_code(self, runresult):
		error_codes = {"OK": 0, "WARNING": 1, "FAIL": 2}
		return error_codes[runresult]
