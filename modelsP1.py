import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class SQLBackend(object):
    """ SQLBackend manages creating the engine and scoped session """

    def __init__(self, DATABASE_URL):
        
        # Check for environment variable
        if not os.environ.get('DATABASE_URL'):
            raise RuntimeError("DATABASE_URL is not set")

        # Set up database
        self.engine = create_engine(DATABASE_URL)
        self.db = scoped_session(sessionmaker(bind=self.engine))