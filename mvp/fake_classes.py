import datetime
import random
import uuid
import wonderwords

from faker import Faker
fake = Faker()


class FakeRobot():
	def __init__(self):
		self.name = f"robot-{self.get_random_word()}"
		self.robotid = self.name
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


class FakeService():
	def __init__(self):
		self.serviceid = uuid.uuid4()
		self.name = f"service-{self.get_random_word()}"
		self.description = f"An awesome service {self.name}"
		self.createddatetime = fake.date_time_this_year()
		self.createdby = self.get_creator()

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

	def get_creator(self):
		creators = ["Admin" for i in range(2)]
		creators.append("Operator")
		return random.choice(creators)


class FakeBusinessProcess():
	def __init__(self, serviceid):
		self.processid = uuid.uuid4()
		self.serviceid = serviceid
		self.name = f"process-{self.get_random_word()}"
		self.description = f"An awesome process {self.name}"
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
	def __init__(self, processid):
		self.transactionid = uuid.uuid4()
		self.name = f"tr-{self.get_random_word()}-{self.get_random_word()}"
		self.processid = processid
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
		self.transactionrunid = uuid.uuid4()
		self.robotid = robotid
		self.runstart = fake.date_time_this_year()
		self.runend = self.runstart + datetime.timedelta(milliseconds=random.randint(15000, 40000))

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()

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
		self.createddatetime = fake.date_time_this_year()
		self.createdby = creator

	def get_random_word(self):
		r = wonderwords.RandomWord()
		return r.word()


class FakeStepRun():
	def __init__(self, transactionrunid, stepid):
		self.steprunid = uuid.uuid4()
		self.stepid = stepid
		self.transactionrunid = transactionrunid
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
