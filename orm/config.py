import json
from pathlib import Path

main_config_file = (Path(__file__).parent / '..' / 'config.json').resolve()
if not main_config_file.exists():
    print(f'Main config file not found: {main_config_file}!')
    exit(1)

class Config:
    db_type = ''
    db_host = ''
    db_port = 0
    db_name = ''
    db_user = ''
    db_password = ''
    db_schema = ''
    api_endpoint = ''
    api_port = 0
    cors_origins = ''
    logs_dir = ''
    screenshots_dir = ''
    mvp_min_runs = 0
    mvp_create_artifacts = False

    def __init__(self, config_file):
        # get all user-defined class attributes
        config_keys = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        try:
            config_dict = json.load(open(config_file, 'r'))
        except Exception as e:
            print(f'Error while reading config file: {e}')
            exit(1)

        # check if all required keys are present
        for key in config_keys:
            if key not in config_dict:
                print(f'Config file must contain value \'{key}\'!')
                exit(255)

        # load config
        for k, v in config_dict.items():
            if k not in config_keys:
                print(f'Config file contains unknown key: \'{k}\'')
                exit(1)
            setattr(self, k, v)

config = Config(main_config_file)
