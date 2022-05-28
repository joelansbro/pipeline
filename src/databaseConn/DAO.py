# this module designates the connection to the external database
# processing module and outboundAPI module must refer to this module for database connectivity



# data to process: 
# reports generated via reportjob.py
# data cleaned from the inboundAPI to raw data location 

# persistence layer - implements the logic of interacting with the database


# I am running this application within a Docker Container, we could open up a port to an outside database for external hosting
# easy as connecting a Port to a cloud Database for example


# the advantage of creating the database outside is we ensure that we don't harcode the database, allowing us to insert any database with a table that fits the schema
# for the test, I will be using SQLite
# SQLite can accept the input I have just tested