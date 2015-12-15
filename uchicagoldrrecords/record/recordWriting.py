def writeNoClobber(record, filepath):
    from os.path import split, isdir, exists
    from json import dump

    path, filename = split(filepath)
    try:
        assert(isdir(path))
        assert(len(filename) > 0)
    except AssertionError:
        return False

    while exists(filepath):
        if filepath[-1].isdigit():
            nextNum = int(filepath[-1])+1
            filepath = filepath[0:-1]+str(nextNum)
        else:
            filepath = filepath+".1"

    with open(filepath, 'w') as f:
        dump(record, f, indent=4, sort_keys=True)
    return True


def instantiateRecord():
    from uchicagoldrrecords.record.recordFields import RecordFields
    record = {}
    for entry in RecordFields():
        record[entry] = ""
    return record


def selectValue(field, existingValue, newValue):
    selection = input("Two Values have tried to populate the " +
                      "same entry: "+field+"\n1) " +
                      existingValue +
                      "\n2) " +
                      newValue+"\nPlease select one via typing either 1 or 2 " +
                      "and hitting enter.\nSelection: ")
    if selection != "1" and selection != "2":
        print("Invalid input. Exiting.")
        exit()
    else:
        if selection == "1":
            return existingValue
        else:
            return newValue


def populateEmpties(record):
    for entry in record:
        if isinstance(record[entry], str):
            if len(record[entry]) == 0:
                value = input("The field \"" + entry +
                              "\" is currently blank. Enter a value, " +
                              "or hit enter to leave it blank.\n")
                record[entry] = value
        elif isinstance(record[entry], dict):
            record[entry] = populateEmpties(record[entry])
    return record


def findEmpties(record, parentPath=""):
    empties = []
    for entry in record:
        newPath = parentPath+"/"+entry
        if isinstance(record[entry], str) and len(record[entry]) == 0:
            empties.append(newPath)
        elif isinstance(record[entry], dict):
            empties += findEmpties(record[entry], newPath)
    return empties


def editRecord(record, key):
    print("Editing entry \""+key+"\"")
    if isinstance(record[key], str):
        newValue = input("Please enter a new value: ")
        record[key] = newValue
    elif isinstance(record[key], dict):
        print("Key value is a dictionary. Please specify a subkey " +
              "specific to that dictionary")
        print("Available subkeys:")
        for subkey in record[key]:
            print(subkey)
        childKey = input("Subkey: ")
        record[key] = editRecord(record[key], childKey)
    else:
        print("Key value is not a recognized editable data type. Sorry!")
    return record


def manualInput(record):
    from json import dumps

    userSuppliedKey = None
    while userSuppliedKey != "":
        print(dumps(record, indent=4, sort_keys=True))
        print("Blank entries:")
        for entry in findEmpties(record):
            print(entry)
        userSuppliedKey = input("Enter the key of any value you would " +
                                "like to manually populate or change.\n" +
                                "Enter on a blank line to continue.\nKey: ")
        if userSuppliedKey != "":
            try:
                editRecord(record, userSuppliedKey)
            except KeyError:
                print("WARNING: That key doesn't appear to be " +
                      "in the record root.")


def stringToBool(string):
    string = string.lower()
    negatives = ['f', 'false', 'no', 'n', 'n/a', '']
    positives = ['t', 'true', 'yes', 'y']
    for term in negatives:
        if string == term:
            return "False"
    for term in positives:
        if string == term:
            return "True"
    return string


def validate(record, validator):
    from re import match

    for entry in validator:
        # Eventually this is where validation of nested values should go
        # if required
        if type(record[entry[0]]) != str:
            continue
        for regex in entry[1]:
            while not match(regex, record[entry[0]]):
                print(entry[0]+" ("+record[entry[0]] +
                      ") does not match against a validation regex! (" +
                      regex+")\nPlease input a new value that conforms "
                      "to the required validation expression.")
                editRecord(record, entry[0])
    return record


def booleanLoop(record, bools):
    for entry in bools:
        suggestion = stringToBool(record[entry])
        if suggestion != record[entry]:
            record[entry] = selectValue(entry, record[entry], suggestion)
    return record


def createSubRecord(record, fields):
    subRecord = {}
    for field in fields:
        subRecord[field] = record[field]
    return subRecord


def meldRecord(record, target, reader, mapper):
    newDict = reader(target)
    for entry in mapper():
        if entry[1] in newDict:
            if record[entry[0]] == "" or record[entry[0]] == newDict[entry[1]]:
                record[entry[0]] = newDict[entry[1]]
            else:
                record[entry[0]] = selectValue(
                    entry[0], record[entry[0]], newDict[entry[1]]
                )


def generateFileEntries(root, item):
    from os.path import join
    from hashlib import sha256

    from uchicagoldr.batch import Batch

    fileInfoDict = {}
    b = Batch(root, item)
    totalDigitalSize = 0
    for item in b.find_items(from_directory=True):
        itemDict = {}
        item.set_accession(item.find_file_accession())
        uid = sha256(join(
              item.get_accession(), item.find_canonical_filepath()
                    ).encode('utf-8')).hexdigest()
        itemDict['fileSize'] = item.find_file_size()
        itemDict['fileMime'] = item.find_file_mime_type()
        itemDict['fileHash'] = item.find_sha256_hash()
        totalDigitalSize += itemDict['fileSize']

        if ".presform" in item.find_file_name():
            presStable = "True"
        else:
            presStable = "False"

        itemDict['fileStable'] = presStable

        fileInfoDict[uid] = itemDict
    return fileInfoDict


def computeTotalFileSizeFromRecord(record):
    totalSize = 0
    for entry in record['fileInfo']:
        totalSize += record['fileInfo'][entry]['fileSize']
    return totalSize
