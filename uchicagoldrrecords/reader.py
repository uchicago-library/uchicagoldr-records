from os.path import isabs
from json import load

from uchicagoldrrecords.record import Record


class Reader(object):
    def __init__(self):
        self.linked_file = None
        self.record = None
        self.record_type = None

    def set_linked_file(self, new_linked_file):
        assert(isabs(new_linked_file))
        self.linked_file = new_linked_file

    def get_linked_file(self):
        return self.linked_file

    def get_record(self):
        return self.record

    def set_record(self, new_record):
        assert(isinstance(new_record, Record))
        self.record = new_record

    def get_record_type(self):
        return self.record_type

    def set_record_type(self, new_record_type):
        assert(isinstance(new_record_type, str))
        self.record_type = new_record_type

    def read(self):
        assert(self.get_linked_file() is not None)

        self.set_record_type('Default')

        with open(self.get_linked_file(), 'r') as f:
            dictionary = load(f)
            newRecord = Record()
            result, conf = newRecord.read_config_file()
            if result:
                newRecord.set_config(conf)
            else:
                raise AssertionError
            newRecord.set_dictionary(dictionary)
            if newRecord.validate():
                return newRecord
            else:
                raise AssertionError
