from uchicagoldrrecords.reader import Reader
from uchicagoldrrecords.record import Record


class DigitalAcquisitionRecordReader(Reader):
    keyMap = [("Accession Number"),
              ("Collection Title"),
              ("Existing Digital Collection"),
              ("Addenda"),
              ("Date sent to DAS", "Sent to DAS On"),
              ("Type"),
              ("Origin"),
              ("Donor First Name", "Donor.First Name"),
              ("Donor Last Name", "Donor.Last Name"),
              ("Donor Address", "Donor.Address"),
              ("Donor Phone", "Donor.Phone"),
              ("Donor Email", "Donor.Email"),
              ("Source First Name", "Source.First Name"),
              ("Source Last Name", "Source.Last Name"),
              ("Source Address", "Source.Address"),
              ("Source Phone", "Source.Phone"),
              ("Source Email", "Source.Email"),
              ("Receipt Letter", "Receipt Letter Required"),
              ("Send Digital Inventory to Donor", "Send Inventory Required"),
              ("Gift Acknowledgement or Deed of Gift", "Gift Acknowledgement Required"),
              ("Access"),
              ("Linear Feet", "Total Physical Size.Linear Feet"),
              ("Boxes", "Total Physical Size.Boxes"),
              ("Volumes", "Total Physical Size.Volumes"),
              ("Restrictions"),
              ("Restriction Comments", "Restriction Comment"),
              ("Description", "Summary"),
              ("Administrative Comments"),
              ("Received By"),
              ("Date Received", "Files Received Date"),
              ("DAS Received By"),
              ("Digital Location"),
              ("P/R/C", "PRC"),
              ("Physical Media"),
              ("Existing Physical Collection"),
              ("EADID"),
              ("Physical Collection Has Finding Aid")
              ]

    keyList = [x[0] for x in keyMap]

    def __init__(self):
        Reader.__init__(self)

    def read(self):
        assert(self.get_linked_file() is not None)

        self.set_record_type('Digital Acquisition')

        with open(self.get_linked_file(), 'r') as f:
            dictionary = self.break_into_dict(f)
        newRecord = \
            self.map_internal_dictionary_to_record(dictionary)
        result, conf = newRecord.read_config_file()
        if result:
            newRecord.set_config(conf)
        else:
            raise AssertionError
        assert(newRecord.validate())
        return newRecord

    def break_into_dict(self, inIO):
        digitalAcquisitionRecord = inIO
        currentField = None
        digitalAcquisitionRecordDict = {}
        fieldValue = ""
        # This is a list of all the terms which are on the accession form,
        # used for delimiting fields

        for line in digitalAcquisitionRecord.readlines():
            # If we haven't hit the field data yet jump to the next line
            if currentField is None and ":" not in line:
                continue
            # If we find a line with a colon and if whats behind it is in the
            # list of keys we are in a new field, grab the whole line even if
            # it has more colons in it
            if ":" in line and line.split(":")[0] in self.keyList:
                # Chomp trailing newlines
                fieldValue = ""
                currentField = line.split(":")[0]
            # Manually strip the front of the line off, its a legitimate field
            # (or a very strange outlier)
                line = line[len(currentField)+1:]
            fieldValue = fieldValue+line
            digitalAcquisitionRecordDict[currentField] = fieldValue
        digitalAcquisitionRecord.close()
        for value in digitalAcquisitionRecordDict:
            # Strip whitespace only from the start/end of values.
            # Leave stuff in the middle for reconstruction later if need be.
            digitalAcquisitionRecordDict[value] = \
                digitalAcquisitionRecordDict[value].strip()
        digitalAcquisitionRecordDict = self._strings_dict_to_data_types(
            digitalAcquisitionRecordDict
        )
        return digitalAcquisitionRecordDict

    def map_internal_dictionary_to_record(self, internal_dict):
        new_record = Record()
        new_record.populate(no_defaults=True)
        for entry in internal_dict:
            assert(entry in self.keyList)
            for mapping in self.keyMap:
                if mapping[0] == entry:
                    mapper = mapping
            if len(mapper) > 1:
                new_record.set_value_from_dotted_key(mapper[1],
                                                     internal_dict[entry])
            else:
                new_record.set_value_from_dotted_key(mapper[0],
                                                     internal_dict[entry])
        return new_record
