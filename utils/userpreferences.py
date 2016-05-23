import os
from ConfigParser import SafeConfigParser

from appdirs import AppDirs


class UserPreferences:

    def __init__(self):
        app_dirs = AppDirs("BlocklyPropClient", "Parallax")

        config_dir = app_dirs.user_config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.config_file = os.path.join(config_dir, '.setting.ini')

        self.configs = SafeConfigParser()

        if os.path.isfile(self.config_file):
            self.configs.read([self.config_file])

        if not self.configs.has_section("user"):
            self.configs.add_section("user")
        if not self.configs.has_section("server"):
            self.configs.add_section("server")

        self.getfloat = self.configs.getfloat
        self.getboolean = self.configs.getboolean

    def set(self, section, option, value=None):
        self.configs.set(section, option, value)
        self.write()

    def write(self):
        # Writing our configuration file
        with open(self.config_file, 'wb') as configfile:
            self.configs.write(configfile)

    def get(self, section, option, default=None):
        if self.configs.has_option(section, option):
            return self.configs.get(section, option)
        return default

    def getint(self, section, option, default=-1):
        if self.configs.has_option(section, option):
            return self.configs.getint(section, option)
        return default
