def ReadAcquisitionRecord(digitalAcquisitionRecordPath):
    digitalAcquisitionRecord = open(digitalAcquisitionRecordPath, 'r')
    currentField = None
    digitalAcquisitionRecordDict = {}
    fieldValue = ""
    # This is a list of all the terms which are on the accession form,
    # used for delimiting fields
    keyList = ["Accession Number",
               "Collection Title",
               "Existing Digital Collection",
               "Addenda",
               "Date of Receipt",
               "Date sent to DAS",
               "Type",
               "Origin",
               "Donor Name",
               "Donor Address",
               "Donor Phone",
               "Donor Email",
               "Source Name",
               "Source Address",
               "Source Phone",
               "Source Email",
               "Receipt Letter",
               "Send Inventory to Donor",
               "Send Digital Inventory to Donor",
               "Gift Acknowledgement or Deed of Gift",
               "Access",
               "Linear Feet",
               "Boxes",
               "Volumes",
               "Digital Size",
               "Other Size",
               "Restrictions",
               "Restriction Comments",
               "Description",
               "Administrative Comments",
               "Received By",
               "Date Received",
               "DAS Received By",
               "DAS Date Received",
               "Digital Location",
               "P/R/C",
               "Physical Media",
               "Existing Physical Collection",
               "EADID",
               "Physical Collection Has Finding Aid"]
    compoundKeys = ['donor', 'source', 'physSize']
    for key in compoundKeys:
        digitalAcquisitionRecordDict[key] = {}
    for line in digitalAcquisitionRecord.readlines():
        # If we haven't hit the field data yet jump to the next line
        if currentField is None and ":" not in line:
            continue
        # If we find a line with a colon and if whats behind it is in the
        # list of keys we are in a new field, grab the whole line even if
        # it has more colons in it
        if ":" in line:
            if line.split(":")[0] in keyList:
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
        if isinstance(digitalAcquisitionRecordDict[value], str):
            # Strip whitespace only from the start/end of values.
            # Leave stuff in the middle for reconstruction later if need be.
            digitalAcquisitionRecordDict[value] = \
                digitalAcquisitionRecordDict[value].strip()
        if value == "Donor Name" or \
                value == "Donor Address" or \
                value == "Donor Phone" or \
                value == "Donor Email":
            digitalAcquisitionRecordDict['donor'][value] = \
                digitalAcquisitionRecordDict[value]
        if value == "Source Name" or \
                value == "Source Address" or \
                value == "Source Phone" or \
                value == "Source Email":
            digitalAcquisitionRecordDict['source'][value] = \
                digitalAcquisitionRecordDict[value]
        if value == "Linear Feet" or \
                value == 'Boxes' or \
                value == 'Volumes' or \
                value == 'Other Size':
            digitalAcquisitionRecordDict['physSize'][value] = \
                digitalAcquisitionRecordDict[value]
    return digitalAcquisitionRecordDict
