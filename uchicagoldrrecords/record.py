from copy import deepcopy
from os.path import isabs
from csv import DictReader
from ast import literal_eval
from re import compile as re_compile
from re import match

from uchicagoldr.batch import Directory
from uchicagoldrconfig.LDRConfiguration import LDRConfiguration

config = LDRConfiguration().read_config_data()


class Record(object):

    allowed_types = ['str', 'dict', 'bool', 'list', 'int', 'float']

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
                        "Validation", "Required For Accession",
                        "Required For Completion"
                        ]
                for req in reqs:
                    assert(req in entry)
                assert(entry['Value Type'] in self.allowed_types)
                assert(entry['Required For Accession'] in ['True', 'False'])
                assert(entry['Required For Completion'] in ['True', 'False'])
                try:
                    re_compile(entry['Validation'])
                except:
                    raise AssertionError
            return True
        except Exception as e:
            print(e)
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

    def populate(self, no_defaults=False):
        assert(self.get_config())
        assert(self.validate_config())
        new_dict = {}
        for row in self.get_config():
            key = self._dotted_to_list(row['Field Name'])
            dataType = row['Value Type']
            if dataType not in self.allowed_types:
                raise ValueError("The following row has an invalid " +
                                 "Value Type!\n{}".format(row))
            else:
                value = eval(dataType+"()")

                if no_defaults:
                    self.set_value_from_key_list(key, value, start=new_dict)
                    continue

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
                self.set_value_from_key_list(key, value, start=new_dict)
        self.set_dictionary(new_dict)

    def validate(self):
        assert(self.validate_config())
        problemFields = []
        for row in self.get_config():
            if row['Validation'] != "":
                key = self._dotted_to_list(row['Field Name'])
                value = self.get_value_from_key_list(key)
                if type(value) != str:
                    value = str(value)
                regex = row['Validation']
                if not match(regex, value):
                    problemFields.append(key)
        if len(problemFields) > 0:
            return (False, problemFields)
        else:
            return (True, problemFields)

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
                    a[key], collisions = self.meld(b[key],
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

    def get_value_from_key_list(self, keyList, start=None):
        if start is None:
            start = self.get_dictionary()
        nextKey = keyList[0]
        if len(keyList) == 1:
            return start[nextKey]
        else:
            assert(nextKey in start)
            return self.get_value_from_key_list(keyList[1:],
                                                start=start[nextKey])

    def set_value_from_key_list(self, keyList, new_value, start=None):
        if start is None:
            start = self.get_dictionary()
        nextKey = keyList[0]
        if len(keyList) == 1:
            start[nextKey] = new_value
            return True
        else:
            assert(nextKey in start)
            self.set_value_from_key_list(keyList[1:], new_value,
                                         start=start[nextKey])

    def blank_value_from_key_list(self, keyList, start=None):
        return self.set_value_from_key_list(keyList, "", start=start)

    def get_value_from_dotted_key(self, dotted_key, start=None):
        return self.get_value_from_key_list(self._dotted_to_list(dotted_key),
                                            start=start)

    def set_value_from_dotted_key(self, dotted_key, new_value, start=None):
        return self.set_value_from_key_list(self._dotted_to_list(dotted_key),
                                            new_value=new_value,
                                            start=start)

    def blank_value_from_dotted_key(self, dotted_key, start=None):
        return self.blank_value_from_key_list(self._dotted_to_list(dotted_key),
                                              start=start)

    def _dotted_to_list(self, inStr):
        assert(isinstance(inStr, str))
        return inStr.split(".")

    def _list_to_dotted(self, inList):
        assert(isinstance(inList, list))
        return ".".join(inList)
