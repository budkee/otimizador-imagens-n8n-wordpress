from io import BytesIO

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps


app = FastAPI()


MAX_SIZE = 2400
QUALITY = 82


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/optimize")
async def optimize(file: UploadFile = File(...)):
    contents = await file.read()

    image = Image.open(BytesIO(contents))

    # Corrige orientação baseada no EXIF
    image = ImageOps.exif_transpose(image)

    # Redimensiona somente se necessário
    image.thumbnail(
        (MAX_SIZE, MAX_SIZE),
        Image.Resampling.LANCZOS
    )

    # JPEG precisa de RGB
    if image.mode != "RGB":
        image = image.convert("RGB")
    # ===========Configs para WEBP===========
    # WebP não trabalha com CMYK
    # if image.mode not in ("RGB", "RGBA"):
    #     image = image.convert("RGBA" if "A" in image.mode else "RGB")

    output = BytesIO()

    # ===========Configs para WEBP===========
    # image.save(
    #     output,
    #     format="WEBP",
    #     quality=QUALITY,
    #     method=6
    # )

    # ===========Configs para JPEG===========
    image.save(
        output,
        format="JPEG",
        quality=QUALITY,
        optimize=True,
        progressive=True
    )

    output.seek(0)

    filename = file.filename or "image"
    # ===========Configs para JPEG===========
    filename = filename.rsplit(".", 1)[0] + ".jpg"
    # ===========Configs para WEBP===========
    # filename = filename.rsplit(".", 1)[0] + ".webp"

    return StreamingResponse(
        output,
        # ===========Configs para WEBP===========
        # media_type="image/webp",
        # ===========Configs para JPEG===========
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )