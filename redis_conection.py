



from fastapi import FastAPI, Depends, HTTPException, Request
import json

app = FastAPI()
@app.on_event("startup")
async def startup_event():
    app.state.redis =   Redis(host="localhost", port=6379)
    app.state.http_client= htppx.AsyncClient()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()


@app.get("/entries")
async def read_item():
    value=app.state.redis.get("entries")

    if value is None:
        response = await app.state.http_client.get("")
        data_str=json.dumps(response.json())
        app.state.redis.set("entries",data_str)

    return json.loads()

