import datetime
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table
from sqlalchemy import Integer, DateTime, Boolean, Text, Float

#create new db
#http://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy
engine = create_engine('postgres://postgres:password@localhost:5433')
conn = engine.connect()
conn.execute("commit")
conn.execute("create database test_db")
conn.close()

#open connection to new db and create the tables
engine = create_engine('postgres://postgres:password@localhost:5433/test_db', echo=True)

metadata=MetaData(bind=engine)

prices_table=Table('Prices',metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('close', Float),
            Column('timestamp', DateTime, default=datetime.datetime.now(), index=True, unique=True)
            )

tweets_table=Table('Tweets',metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('user_id', Integer, index=True),
            Column('text', Text),
            Column('retweet', Boolean),
           	Column('retweet_count', Integer),
            Column('timestamp', DateTime, default=datetime.datetime.now(), index=True),
            Column('sentiment', Float),
            
            )

users_table=Table('Users',metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('username', Text, unique=True),
			Column('followers', Integer),
			Column('following', Integer),
            )

metadata.create_all()