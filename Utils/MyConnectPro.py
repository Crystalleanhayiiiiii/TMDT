from sqlalchemy import create_engine, Column, Integer, String , text
from sqlalchemy.orm import sessionmaker

class MyConnectPro:
    def __init__(self ,user , password, database, host , port ):
        self.host = host
        self.username = user
        self.password = password
        self.database = database
        self.port = port

    def connect(self):
        connection_url = f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(connection_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        session = self.Session()
        return session

    def execute_query(self, query):
        if not self.engine or not self.Session:
            self.connect()
        session = self.Session()
        try:
            result = session.execute(text(query))
            return result.fetchall()
        finally:
            session.close()
    