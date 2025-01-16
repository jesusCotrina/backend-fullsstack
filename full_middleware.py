import redis
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import jwt
import time

# Configura Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

app = FastAPI()
ALLOWED_ORIGIN = "https://front-jc.netlify.app"
SECRET_KEY = "my-secret-key"
UNAUTHENTICATED_ROUTES = ["/public", "/token"]
REQUEST_LIMIT = 10000  # Límite de solicitudes
BLOCK_TIME = 3600  # Tiempo de bloqueo en segundos (ej. 1 hora)

@app.middleware("http")
async def verify_jwt(request: Request, call_next):
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    token = request.headers.get("Authorization")
    client_ip = request.client.host  # Obtiene la IP del cliente

    # Verificar el origen y referer
    if (origin != ALLOWED_ORIGIN or referer is None or not referer.startswith(ALLOWED_ORIGIN)):
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Verificar si la IP está bloqueada
    if redis_client.exists(f"block:{client_ip}"):
        raise HTTPException(status_code=403, detail="IP address is blocked due to too many requests")

    # Contar las solicitudes
    request_count_key = f"request_count:{client_ip}"
    request_count = redis_client.incr(request_count_key)

    # Establecer tiempo de expiración si es la primera solicitud
    if request_count == 1:
        redis_client.expire(request_count_key, 3600)  # Resetea el contador cada hora

    # Comprobar si la IP ha superado el límite
    if request_count > REQUEST_LIMIT:
        # Bloquear la IP
        redis_client.set(f"block:{client_ip}", 1, ex=BLOCK_TIME)  # Bloquear por 1 hora
        raise HTTPException(status_code=429, detail="Too Many Requests")

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
