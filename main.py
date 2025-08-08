from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints import capture, segmentation, ocr, genetico, edit_club_players

app = FastAPI(title="FUTBIN API", debug=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(capture.router, prefix="/api")
app.include_router(segmentation.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")
app.include_router(genetico.router, prefix="/api")
app.include_router(edit_club_players.router, prefix="/api")