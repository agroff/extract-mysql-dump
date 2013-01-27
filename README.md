
#Extract MySQL Dump

This is a command line utility (for Python 3.3) intended to extract a mysql dump file. Since dump files often contain many databases and can be very large, I created this to help me break my database dumps into smaller pieces in order to get the parts I am interested in. I also created it to help me learn Python.

I am sharing this in the hope that it will be useful to someone else, and also to receive feedback and improve my Python skills. Since I created it to work with my sql dumps, there's a good chance it won't work with yours. Hopefully over time it will improve to work with all MySQL dumps, but right now it is unlikely.

Hopefully the help output is detailed enough to let you use the program immediately:

    usage: extractBackup.py [-h] [-i] [-x] [-v] [-r] sql_dump

    Extract data from a SQL dump file

    positional arguments:
      sql_dump        The SQL Dump file you would like to extract or inspect

    optional arguments:
      -h, --help      show this help message and exit
      -i, --inspect   Inspects the backup file, printing a list of databases and
                      tables and exits
      -x, --extended  Extended extract. Includes individual files for tables and
                      procedures
      -v, --verbose   Shows the output from inspect, but actually does the
                      extraction instead of exiting.
      -r, --remove    Removes the files created by the extraction for a given dump

##More Usage Details

You can test out the script to see if it helps you like so:

Create a mysql dump:

`mysqldump -u <you> -p<your password> --all-databases --routines > local.sql`

Inspect your dump:

`python3.3 extractBackup.py -i local.sql`

Extract it:

`python3.3 extractBackup.py -xv local.sql`

The -v option will print output as it is encountered. The -x option will create files for each table and a procedures file for each database that has them. Look through the output to ensure it is correct before using it.

Find any files you need in the output. For this example the output will be in a folder called `local-extract/`. Copy/move any files you need to another location, since we'll remove all the generated files in the next step.

`python3.3 extractBackup.py -r local.sql`

Now all the files it created will be removed.

##Other Methods
I assume there are other utilities that do a better job of what this attempts to do, but I haven't found them yet. If you are just interested in restoring or extracting a single database, this blog has some good info on that:

http://pento.net/2009/04/16/extracting-a-database-from-a-mysqldump-file/

If you know of other utilities for extracting MySQL dumps, let me know and we can link them here.

##Contribution / Roadmap

Feel free to contribute to make this tool better. In the near future my main vision is to make this tool work better for a variety of MySql Dumps with various options.

Later, perhaps we can add some options for processing, to remove `DROP TABLE` statements, change the definer of stored procedures, etc.