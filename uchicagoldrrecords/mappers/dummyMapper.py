def DummyMapper():
    from uchicagoldrRecords.record.recordFields import RecordFields

    dummyMap = []
    for entry in RecordFields():
        dummyMap.append((entry, entry))
    return dummyMap
