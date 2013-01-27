#Written for Python 3.3
import argparse
import os
import re
import shutil
import sys

def inspectLine(line):
    if args.inspect or args.verbose:
        print(line)

def getDirectory():
    return args.sql_dump.replace('.sql', '') + '-extract'

def getTableDirectory():
    return os.path.join(getDirectory(), currentDb + '-tables')

def ensureFolder():
    directory = getDirectory()

    if not os.path.exists(directory):
        os.makedirs(directory)

def removeEmptyExtra(extraFile):
    file = open(extraFile, "r", encoding="ISO-8859-4");
    contents = file.read();
    file.close()
    contents = re.sub(r'^--.*$', r'', contents, flags=re.MULTILINE)
    contents = re.sub(r'^\s*USE\s*`[^`]+`;\s*$', r'', contents, flags=re.MULTILINE)
    contents = re.sub(r'\s*', r'', contents, flags=re.MULTILINE)
    if contents == '':
        if args.verbose:
            print("Removing empty file: '", extraFile, "'... ")
        os.remove(extraFile)

def getProcedureFile():
    return os.path.join(getDirectory(), currentDb + '.procedures.sql')

def writeOneLine(line, file, mode):
    if args.inspect:
        return
    output = open(file, mode)
    output.write(line)
    output.close()

def writeLine(line):
    if args.inspect:
        return

    ensureFolder();
    directory = getDirectory()

    #write to the database or misc files
    file = os.path.join(directory, currentDb)
    if currentDb == '':
        file = os.path.join(directory, 'header')
        if headerPassed:
            file =  os.path.join(directory, 'footer')

    file += '.sql'

    mode = 'a'

    writeOneLine(line, file, mode)

    if not args.extended:
        return
    if currentDb == '':
        return
    if not inProcedure and currentTable == '':
        return

    tableDir = getTableDirectory()
    if not os.path.exists(tableDir):
        os.makedirs(tableDir)

    file = os.path.join(tableDir, currentDb + '.table.' + currentTable + '.sql')

    if inProcedure:
        file = getProcedureFile()

    writeOneLine(line, file, mode)



################
# End functions.
################

##################################
#  Define Arguments
##################################
parser = argparse.ArgumentParser(description="""
Extract data from a SQL dump file
""")


parser.add_argument("-i", "--inspect",
    help="Inspects the backup file, printing a list of databases and tables and exits",
    action="store_true")
parser.add_argument("-x", "--extended",
    help="Extended extract. Includes individual files for tables and procedures",
    action="store_true")
parser.add_argument("-v", "--verbose",
    help="Shows the output from inspect, but actually does the extraction instead of exiting.",
    action="store_true")
parser.add_argument("-r", "--remove",
    help="Removes the files created by the extraction for a given dump",
    action="store_true")


parser.add_argument('sql_dump', help="The SQL Dump file you would like to extract or inspect")

args = parser.parse_args()
##################################
# End of arguments
##################################

#make sure file doesn't contain a /
if "/" in args.sql_dump:
    print("""
    `/` Detected in file. Please use a local file.

    Aborting.
     """)
    sys.exit(1)


#remove previous extract
if not args.inspect:
    if os.path.exists(getDirectory()):
        shutil.rmtree(getDirectory())

if args.remove:
    print ("Directory " + getDirectory() + " removed.")
    sys.exit(0)

sql_dump = open(args.sql_dump, "r", encoding="ISO-8859-4")

database_re = re.compile(r"Database:\s*`([^`]+)`")
procedure_re = re.compile(r"CREATE.+PROCEDURE\s*`([^`]+)`")
procedures_start_re = re.compile(r"Dumping routines")
table_re = re.compile(r"(?:DROP TABLE|CREATE\s+TABLE|Table\s+structure\s+for).+`([^`]+)`")
end_re = re.compile(r"^\/\*!\d+\sSET\s+(?:SQL|TIME)")

count = 0
procCount = 0
tableCount = 0
dbCount = 0
currentDb = ''
currentTable = ''
inProcedure = False
headerPassed = False
usedDbs = {}
usedTables = {}

for line in sql_dump:
    count += 1

    isDb = database_re.search(line)
    isProc = procedure_re.search(line)
    isTable = table_re.search(line)
    isEnd = end_re.search(line)
    isProcStart = procedures_start_re.search(line)

    if isDb:
        currentDb = isDb.group(1)

        if not currentDb in usedDbs:
            tableCount = 0
            procCount = 0

        usedDbs[currentDb] = 1
        inProcedure = False
        headerPassed = True
        inspectLine("\nStart Database: \n" + currentDb)
        dbCount += 1

    if isEnd:
        if dbCount > 0:
            currentDb = ''

    if isProcStart:
        inProcedure = True

    if isProc:
        if procCount == 0:
            inspectLine("\n" + " " * 4 + "Procedures: ")
        inspectLine(" " * 8 + isProc.group(1));
        procCount += 1

    if isTable:
        if tableCount == 0:
            inspectLine("\n" + "  " + "Tables: ")
        currentTable = isTable.group(1)
        inProcedure = False
        if not currentTable in usedTables:
            inspectLine(" " * 4 + currentTable);
            tableCount += 1
            usedTables[currentTable] = 1

        #print(count)
    writeLine(line)
sql_dump.close();


#Cleanup extras files
if not args.inspect:
    path = getDirectory()
    listing = os.listdir(path)
    for infile in listing:
        if ".procedures.sql" in infile:
            removeEmptyExtra(os.path.join(path, infile))

