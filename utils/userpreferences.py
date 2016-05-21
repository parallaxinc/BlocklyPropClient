import os
from ConfigParser import SafeConfigParser

from appdirs import AppDirs


class UserPreferences():

    def __init__(self):
        app_dirs = AppDirs("BlocklyPropClient", "Parallax")

        config_dir = app_dirs.user_config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.config_file = os.path.join(config_dir, '.setting.ini')

        print(self.config_file)
        self.configs = SafeConfigParser()

        # self.configs['user'] = {}
        # self.configs['server'] = {}

        if os.path.isfile(self.config_file):
            self.configs.read([self.config_file])

        self.configs.add_section("user")
        self.configs.set("user", "login", 'michel@creatingfuture.eu')
        # self.add_section("server")

        self.write()

    def write(self):
        # Writing our configuration file
        with open(self.config_file, 'wb') as configfile:
            self.configs.write(configfile)
