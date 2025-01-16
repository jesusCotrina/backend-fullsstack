import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

#load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_DIALECT = os.getenv('DB_DIALECT')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_USER = os.getenv('DB_USER')
DB_PORT = os.getenv('DB_PORT')

#URL_CONNECTION = '{}://{}:{}@{}/{}'.format(DB_DIALECT, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

URL_CONNECTION=f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("url",URL_CONNECTION)
engine = create_engine(URL_CONNECTION)
# engine = create_engine(
#     DATABASE_URL,
#     pool_size=10,               # Número máximo de conexiones abiertas
#     max_overflow=20,            # Número máximo de conexiones adicionales que se pueden abrir si el pool está lleno
#     pool_timeout=30,            # Tiempo de espera para obtener una conexión antes de lanzar un error
#     pool_recycle=1800           # Tiempo de vida útil de una conexión en segundos
# )

localSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()