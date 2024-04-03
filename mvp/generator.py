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
    fake_process_list = []
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

    def genNewRobots(self, cnt=10):
        new_fake_robots = [mvp.FakeRobot().__dict__ for i in range(random.randint(cnt // 2, cnt))]
        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/robots'
            response = requests.post(url, json={"robots": APICore.json_reserialize(new_fake_robots)})
            if response.status_code != 200:
                raise ConnectionError(f'API Error: {response.status_code} {response.text}')

            for i in range(len(new_fake_robots)):
                robot_with_id = new_fake_robots[i]
                robot_with_id['robotid'] = response.json()['ids'][i]
                self.fake_robot_list.append(robot_with_id)

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

    def genNewProcesses(self, cnt=5):
        new_fake_processes = [mvp.FakeProcess().__dict__ for i in range(random.randint(cnt // 2, cnt))]
        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/processes'
            response = requests.post(url, json={"processes": APICore.json_reserialize(new_fake_processes)})
            if response.status_code != 200:
                raise ConnectionError(f'API Error: {response.status_code} {response.text}')

            for i in range(len(new_fake_processes)):
                process_with_id = new_fake_processes[i]
                process_with_id['processid'] = response.json()['ids'][i]
                self.fake_process_list.append(process_with_id)

        except Exception as e:
            print(f'Error while inserting processes: {e}')
            exit(1)

    def getExistingProcesses(self):
        self.fake_process_list.clear()
        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/processes'
            response = requests.get(url)
            if response.status_code != 200:
                raise ConnectionError(f'API Error: {response.status_code} {response.text}')
            self.fake_process_list.extend(response.json()['processes'])

        except Exception as e:
            print(f'Error while getting processes: {e}')
            exit(1)

    def workOnProcesses(self):
        self.getExistingProcesses()
        if not self.fake_process_list:
            self.genNewProcesses()

    def genNewServices(self, cnt=5):
        self.fake_service_list.clear()
        new_fake_services = []

        # for each process create services
        for process in self.fake_process_list:
            new_fake_services.extend([mvp.FakeService(process['processid']).__dict__ for i in
                                      range(random.randint(cnt // 2, cnt))])

        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/services'
            response = requests.post(url, json={"services": APICore.json_reserialize(new_fake_services)})
            if response.status_code != 200:
                raise ConnectionError(f'API Error: {response.status_code} {response.text}')

            for i in range(len(new_fake_services)):
                service_with_id = new_fake_services[i]
                service_with_id['serviceid'] = response.json()['ids'][i]
                self.fake_service_list.append(service_with_id)

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
        self.workOnProcesses()
        self.getExistingServices()
        if not self.fake_service_list:
            self.genNewServices()

    def genNewTrans(self, cnt=5):
        self.fake_transaction_list.clear()
        new_fake_transactions = []

        # for each service create transactions
        for service in self.fake_service_list:
            new_fake_transactions.extend([mvp.FakeTransaction(service['serviceid']).__dict__ for i in
                                          range(random.randint(cnt // 2, cnt))])

        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/transactions'
            response = requests.post(url, json={"transactions": APICore.json_reserialize(new_fake_transactions)})
            if response.status_code != 200:
                raise ConnectionError(f'API Error: {response.status_code} {response.text}')

            for i in range(len(new_fake_transactions)):
                transaction_with_id = new_fake_transactions[i]
                transaction_with_id['transactionid'] = response.json()['ids'][i]
                self.fake_transaction_list.append(transaction_with_id)

        except Exception as e:
            print(f'Error while inserting transactions: {e}')
            exit(1)

    def getExistingTrans(self):
        self.fake_transaction_list.clear()
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
        self.workOnServices()
        self.getExistingTrans()
        if not self.fake_transaction_list:
            self.genNewTrans()

    def genNewTransSteps(self, cnt=10):
        self.fake_transaction_step_list.clear()
        new_fake_steps = []

        # for each transaction create steps
        for transaction in self.fake_transaction_list:
            new_fake_steps.extend([mvp.FakeStepInfo(transaction['transactionid']).__dict__ for i in
                                   range(random.randint(cnt // 2, cnt))])
        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/steps'
            response = requests.post(url, json={"steps": APICore.json_reserialize(new_fake_steps)})
            if response.status_code != 200:
                raise ConnectionError(f'API Error: {response.status_code} {response.text}')

            for i in range(len(new_fake_steps)):
                step_with_id = new_fake_steps[i]
                step_with_id['stepid'] = response.json()['ids'][i]
                self.fake_transaction_step_list.append(step_with_id)

        except Exception as e:
            print(f'Error while inserting steps: {e}')
            exit(1)

    def getExistingTransSteps(self):
        self.fake_transaction_step_list.clear()
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
        self.workOnTrans()
        self.getExistingTransSteps()
        if not self.fake_transaction_step_list:
            self.genNewTransSteps()

    def doRuns(self):
        runs = []

        # Для каждой транзакции делаем по 10-20 запусков
        for fake_transaction in self.fake_transaction_list:
            for i in range(random.randint(config.mvp_min_runs, config.mvp_min_runs * 2)):
                robot = random.choice(self.fake_robot_list)
                fake_transaction_run = mvp.FakeTransactionRun(fake_transaction['transactionid'],
                                                              robot['robotid']).__dict__
                fake_transaction_run['step_runs'] = []

                # И для каждого запуска транзакции заполняем его шаги
                fake_transaction_run["runresult"] = "OK"
                for fake_transaction_step in self.fake_transaction_step_list:
                    if fake_transaction_step['transactionid'] == fake_transaction['transactionid']:
                        fake_transaction_step_run = mvp.FakeStepRun(fake_transaction_step['stepid']).__dict__

                        # logs and screenshots
                        fake_transaction_step_run['logid'] = self.genLog() if config.mvp_create_artifacts else str(
                            uuid.uuid4())
                        fake_transaction_step_run['screenshotid'] = self.genScreenshot(
                            fake_transaction_step_run['runresult']) if config.mvp_create_artifacts else str(
                            uuid.uuid4())

                        fake_transaction_run['step_runs'].append(fake_transaction_step_run)
                        if fake_transaction_step_run['runresult'] != "OK":  # logical and
                            fake_transaction_run["runresult"] = fake_transaction_step_run['runresult']

                # work on logs
                fake_transaction_run['logid'] = self.concatLogs() if config.mvp_create_artifacts else str(uuid.uuid4())
                runs.append(fake_transaction_run)

        try:
            url = f'http://{config.api_endpoint}:{config.api_port}/runs'
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
    filler.workOnTransSteps()  # cascade
    filler.doRuns()


if __name__ == '__main__':
    main()
