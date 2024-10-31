files = ['customer',
         'lineitem',
         'nation',
         'orders',
         'part',
         'partsupp',
         'region',
         'supplier',]


def TblToCsv(filename):
    csv = open("".join([filename, ".csv"]), "w+")
    tbl = open("".join([filename, ".tbl"]), "r")
    lines = tbl.readlines()
    for line in lines:
        line = line.replace("|", "")
        csv.write(line)
    tbl.close()
    csv.close()
    return

for file in files:
    TblToCsv(file, None)