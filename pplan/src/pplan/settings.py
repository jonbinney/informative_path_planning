import os.path
import yaml

class PPlanSettings:
    def __init__(self, run_dir):
        # read variables in from the settings file for this run
        self.data_dir = os.path.join(run_dir, 'data')
        setting_dict = {}
        execfile(os.path.join(run_dir, 'settings.py'), {}, setting_dict)
        for k in setting_dict.keys():
            self.__dict__[k] = setting_dict[k]

