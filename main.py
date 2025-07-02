from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import requests
import io
from PIL import Image
import uvicorn

app = FastAPI()

DEEPAI_API_URL = "https://api.deepai.org/api/nsfw-detector"
DEEPAI_API_KEY = "b7be32e8-f077-4405-81f6-786e24213df8"

@app.post("/moderate")
async def moderate_image(file: UploadFile):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Only JPG/PNG images!")
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image.verify()

        headers = {'api-key': DEEPAI_API_KEY}
        files = {'image': image_data}
        response = requests.post(DEEPAI_API_URL, files=files, headers=headers)
        response_data = response.json()

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Moderation service error")

        nsfw_score = response_data.get('output', {}).get('nsfw_score', 0)

        if nsfw_score > 0.7:
            return JSONResponse(
                status_code=200,
                content={"status": "REJECTED", "reason": "NSFW content"})
        else:
            return JSONResponse(
                status_code=200,
                content={"status": "OK"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)