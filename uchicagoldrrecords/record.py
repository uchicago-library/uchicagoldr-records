from copy import deepcopy
from os.path import isabs
from csv import DictReader
from ast import literal_eval

from uchicagoldr.batch import Directory
from uchicagoldrconfig.LDRConfiguration import LDRConfiguration

config = LDRConfiguration().read_config_data()


class Record(object):
    def __init__(self, config_override_location=None):
        self.directory = None
        self.dictionary = {}
        if config_override_location is not None:
            self.set_config_location(config)
        else:
            self.config_location = \
                config['records']['record_configuration_path']
        self.config = None

    def set_directory(self, new_directory):
        assert(isinstance(new_directory, Directory))
        self.directory = new_directory.get_directory_path()

    def get_directory(self):
        return self.directory

    def set_dictionary(self, newDict):
        assert(isinstance(newDict, dict))
        self.dictionary = newDict

    def get_dictionary(self):
        return self.dictionary

    def get_config_location(self):
        return self.config_location

    def set_config_location(self, new_config_location):
        assert(isabs(new_config_location))
        self.config_location = new_config_location

    def get_config(self):
        return self.config

    def set_config(self, new_config):
        if self.validate_config(new_config):
            self.config = new_config
            return True
        else:
            return False

    def validate_config(self, config=None):
        if config is None:
            config = self.get_config()
        try:
            assert(isinstance(config, list))
            for entry in config:
                assert(isinstance(entry, dict))
                reqs = ["Field Name", "Value Type", "Default Value",
                        "Validation", "Required for Accession",
                        "Required For Completion"
                        ]
                for req in reqs:
                    assert(req in entry)
            return True
        except:
            return False

    def read_config_file(self):
        with open(self.get_config_location(), 'r') as f:
            try:
                reader = DictReader(f)
                rows = []
                for row in reader:
                    rows.append(row)
                return (True, rows)
            except Exception as e:
                return (False, e)

    def populate(self):
        assert(self.get_config())
        assert(self.validate_config())
        new_dict = {}
        for row in self.get_config():
            key = row['Field Name']
            dataType = row['Value Type']
            if dataType not in ['str', 'dict', 'bool', 'list', 'int', 'float']:
                raise ValueError("The following row has an invalid " +
                                 "Value Type!\n{}".format(row))
            else:
                value = eval(dataType+"()")
                if row['Default Value'] != "":
                    if type(value) != str:
                        try:
                            if type(literal_eval(row['Default Value'])) == \
                                    type(value):
                                value = literal_eval(row['Default Value'])
                            else:
                                raise ValueError("The following row claims a " +
                                                 "Value Type different from " +
                                                 "the provided default value!" +
                                                 "\n{}".format(row))
                        except:
                            raise ValueError("A default value is malformed")
                    else:
                        value = row['Default Value']
                new_dict[key] = value
        self.set_dictionary(new_dict)

    def meld(self, b, a=None, path=None, collisions=None):
        if collisions is None:
            collisions = []
        if path is None:
            path = []
        if a is None:
            a = deepcopy(self.get_dictionary())
        # http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    a[key], collisions = self.merge(b[key],
                                                    a[key],
                                                    path + [str(key)],
                                                    collisions)
                elif a[key] == b[key]:
                    pass
                else:
                    if a[key] == "":
                        a[key] = b[key]
                    else:
                        collisions.append(path + [str(key)])
            else:
                pass
        if len(collisions > 0):
            return (False, collisions)
        else:
            return (True, a)
