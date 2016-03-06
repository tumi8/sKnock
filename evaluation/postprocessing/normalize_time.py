import sys, getopt, csv, os


def normalize_time(file, column):
    new_rows = []

    with open(file, 'rb') as baconFile:
        reader = csv.reader(baconFile)

        minTime = None
        for row in reader:
            if minTime is None:
                minTime = float(row[column])
            else:
                minTime = min(minTime, float(row[column]))

        print "Found minimum time: %s" % minTime

        baconFile.seek(0)
        for row in reader:
            new_row = row
            new_row[column] = float(row[column]) + minTime
            new_rows.append(new_row)

    print "Normalized data in RAM"
    print "Writing to file..."

    normalized_file = ''.join((os.path.splitext(file)[0], "_normalized.csv"))

    with open(normalized_file, 'wb') as baconFile:
        writer = csv.writer(baconFile)
        writer.writerows(new_rows)



def usage():
    print "Usage: normalize_time.py [-c <column index with time data (starting by 0)>] <csv file>"
    sys.exit(2)

def parseArguments(argv):
    column = 0
    try:
        opts, args = getopt.getopt(argv, "c:")
        for opt, arg in opts:
            if opt in ("-c"):
                column = int(arg)
        if len(args) == 1:
            file = args[0]
        else:
            usage()
    except getopt.GetoptError:
        usage()

    return file, column


if __name__ == '__main__':
    normalize_time(*parseArguments(sys.argv[1:]))
