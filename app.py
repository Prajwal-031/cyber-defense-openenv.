import os
import uvicorn
from server import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="127.0.0.1", port=port)
