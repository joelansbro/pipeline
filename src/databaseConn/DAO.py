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

from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.base import Engine

from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(bind=engine)
session = Session()


def fetch_single_article(engine: Engine, uuid) -> Optional[List[dict]]:
    """ The example provided fetches a list of dicts
        Which *should* work to return a single article
    """
    result = engine.execute(
        text(
            """
            SELECT * FROM articles
            WHERE id = {};
            """.format(uuid)
        )
    )
    rows = [dict(row) for row in result.fetchall()]
    LOGGER.info(f"Selected {result.rowcount} rows: {rows}")
    return rows