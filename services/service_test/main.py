from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import os


app = FastAPI()

print( app )

@app.get("/")
async def root():
    return JSONResponse(content={"message": os.getenv('CONTENT')})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT')))

