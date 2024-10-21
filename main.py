from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import scripts.crud as crud
from scripts.database import engine, localSession
from scripts.schemas import UserData, UserId
from scripts.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
ALLOWED_ORIGIN="https://front-jc.netlify.app"

origin = [
    "https://front-jc.netlify.app",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
    )

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def root():
    return 'Hi, my name is FastAPI'


@app.get('/api/users/', response_model=list[UserId])
def get_users(request: Request,db: Session = Depends(get_db)):
    referer = request.headers.get("referer")
    if not referer or not referer.startswith(ALLOWED_ORIGIN):
        raise HTTPException(status_code=403, detail="Access from this origin is not allowed")
    
    return crud.get_users(db=db)


@app.get('/api/users/{id:int}', response_model=UserId)
def get_user(id, db: Session = Depends(get_db)):
    user_by_id = crud.get_user_by_id(db=db, id=id) 
    if user_by_id:
        return user_by_id 
    raise HTTPException(status_code=404, detail='User not Found!!')


@app.post('/api/users/', response_model=UserId)
def create_user(user: UserData, db: Session = Depends(get_db)):
    check_name = crud.get_user_by_name(db=db, name=user.name)
    if check_name:
        raise HTTPException(status_code=400, detail='User already exist.')
    return crud.create_user(db=db, user=user)

