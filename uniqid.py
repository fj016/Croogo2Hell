# Mimicking php uniqid implementation and adding some helpers to achieve our goals

import time

def generate_uniqid(prefix="", debug=False):
    current_time = time.time()
    sec = int(current_time)
    usec = int((current_time - sec) * 1e6)
    uniqid = "{}{:08x}{:05x}".format(prefix, sec, usec)
    if debug == True:
        return uniqid,current_time # Return a tuple containing the uniqid and the time that generated it, for debug purposes
    else:
        return uniqid

def generate_uniqid_ts(sec, usec, prefix=""):
    uniqid = "{}{:08x}{:05x}".format(prefix, sec, usec)
    return uniqid

def uniqid_to_epoch(uniqid, prefix=""):
    time_sec_hex = uniqid[len(prefix):len(prefix) + 8]
    time_usec_hex = uniqid[len(prefix) + 8:len(prefix) + 13]
    time_sec = int(time_sec_hex, 16)
    time_usec = int(time_usec_hex, 16)
    full_epoch = time_sec + (time_usec / 1e6)

    return full_epoch

def uniqids_between(id1, id2, prefix="", large=False):
    time1_sec = int(id1[len(prefix):len(prefix) + 8], 16)
    time1_usec = int(id1[len(prefix) + 8:len(prefix) + 13], 16)
    time2_sec = int(id2[len(prefix):len(prefix) + 8], 16)
    time2_usec = int(id2[len(prefix) + 8:len(prefix) + 13], 16)

    if large:
        time1_sec -= 2
        time2_sec += 2

    uniqids = []
    while (time1_sec < time2_sec) or (time1_sec == time2_sec and time1_usec < time2_usec):
        uniqid = "{}{:08x}{:05x}".format(prefix, time1_sec, time1_usec)
        uniqids.append(uniqid)
        time1_usec += 1
        # handle rolover
        if time1_usec >= 1e6:
            time1_usec = 0
            time1_sec += 1

    return len(uniqids), uniqids


def uniqids_around_timestamp(timestamp, rangeplus=0, rangeminus=0, prefix=""):
    start_sec = int(timestamp - rangeminus)
    start_usec = int((timestamp - start_sec - rangeminus) * 1e6)

    end_sec = int(timestamp + rangeplus)
    end_usec = int((timestamp + rangeplus - end_sec) * 1e6)

    uniqids = []

    current_sec = start_sec
    current_usec = start_usec

    while (current_sec < end_sec) or (current_sec == end_sec and current_usec <= end_usec):
        uniqid = generate_uniqid_ts(current_sec, current_usec, prefix)
        uniqids.append(uniqid)

        # + 1us
        current_usec += 1

        # handle rollover
        if current_usec >= 1e6:
            current_usec = 0
            current_sec += 1

    return uniqids