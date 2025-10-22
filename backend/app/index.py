from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from routers.main import *


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("index:app",reload=True)

handler = Mangum(app)