from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI()

print( app )

@app.get("/")
async def root():
    return JSONResponse(content={"message": "Hello Instruct"})

