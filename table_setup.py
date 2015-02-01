import datetime
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table
from sqlalchemy import Integer, DateTime, Boolean, Text, Float, BigInteger

#create new db
#http://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy
engine = create_engine('postgres://postgres:postgres@localhost:5432')
conn = engine.connect()
conn.execute("commit")
conn.execute("create database twitterbot")
conn.close()

#open connection to new db and create the tables
engine = create_engine('postgres://postgres:postgres@localhost:5432/twitterbot', echo=True)

metadata=MetaData(bind=engine)

prices_table=Table('prices',metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('close', Float),
            Column('timestamp', DateTime, default=datetime.datetime.now(), index=True, unique=True)
            )

tweets_table=Table('tweets',metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('user_id', Integer, index=True),
            Column('text', Text),
            Column('retweet', Boolean),
           	Column('retweet_count', Integer),
            Column('timestamp', DateTime, default=datetime.datetime.now(), index=True),
            Column('sentiment', Float),
            
            )

users_table=Table('users',metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('user_id', BigInteger, unique=True),
            Column('username', Text, unique=True),
			Column('followers', Integer),
			Column('following', Integer),
            )

metadata.create_all()