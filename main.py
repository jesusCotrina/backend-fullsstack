from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import scripts.crud as crud
from scripts.database import engine, localSession
from scripts.schemas import UserData, UserId
from scripts.models import Base
from jose import jwt, JWTError


Base.metadata.create_all(bind=engine)

app = FastAPI()
ALLOWED_ORIGIN="https://front-jc.netlify.app"
UNAUTHENTICATED_ROUTES = ["/", "/public-endpoint"]
SECRET_KEY = ""

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


@app.get('/api/users/', response_model=list[UserId])
def get_users(request: Request,db: Session = Depends(get_db)):
    referer = request.headers.get("referer")
    if not referer or not referer.startswith(ALLOWED_ORIGIN):
        raise HTTPException(status_code=403, detail="Access from this origin is not allowed")
    
    return crud.get_users(db=db)
    
@app.middleware("http")
async def verify_jwt(request: Request, call_next):
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    token = request.headers.get("Authorization")

    # Verificar el origen y referer
    if (origin != ALLOWED_ORIGIN or referer is None or not referer.startswith(ALLOWED_ORIGIN)):
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Si la ruta no necesita autenticación, pasar la solicitud
    if request.url.path in UNAUTHENTICATED_ROUTES:
        response = await call_next(request)
        return response

    # Verificar el token
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Token missing or invalid")

    # Extraer el token
    token = token.split(" ")[1]

    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user = payload  # Guardar información del usuario en el request
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")

    response = await call_next(request)
    return response


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

