import sys

from sanic import Sanic
from sanic.request import Request
from sanic.response import JSONResponse

from static.utils import Model, decode_image, encode_image_to_base64, preprocess_replace_bg_image

STATIC_PATH: str = "static"
VERSION: str = "1.0.0"
models: list = []

app = Sanic("BG-Remove-API")
app.static("static", "static")


@app.get("/")
async def get_root(request: Request) -> JSONResponse:
    return JSONResponse(
        body={
            "statusText" : "Root Endpoint of BG-Remove-API",
            "version" : VERSION,
        },
        status=200,
    )


@app.get("/<infer_type:str>")
async def get_processing(request: Request, infer_type: str) -> JSONResponse:
    if infer_type == "remove":
        return JSONResponse(
            body={
                "statusText" : "Background Removal Endpoint of BG-Remove-API",
                "version" : VERSION,
            },
            status=200,
        )
    elif infer_type == "replace":
        return JSONResponse(
            body={
                "statusText" : "Background Replacement Endpoint of BG-Remove-API",
                "version" : VERSION,
            },
            status=200,
        )
    else:
        return JSONResponse(
            body={
                "statusText" : "Invalid Infer Type",
                "version" : VERSION,
            },
            status=400,
        )


@app.get("/<infer_type:str>/li")
async def get_processing_li(request: Request, infer_type: str) -> JSONResponse:
    if infer_type == "remove":
        return JSONResponse(
            body={
                "statusText" : "Lightweight Background Removal Endpoint of BG-Remove-API",
                "version" : VERSION,
            },
            status=200,
        )
    elif infer_type == "replace":
        return JSONResponse(
            body={
                "statusText" : "Lightweight Background Replacement Endpoint of BG-Remove-API",
                "version" : VERSION,
            },
            status=200,
        )
    else:
        return JSONResponse(
            body={
                "statusText" : "Invalid Infer Type",
                "version" : VERSION,
            },
            status=400,
        )
    

@app.post("/<infer_type:str>")
async def post_processing(request: Request, infer_type: str) -> JSONResponse:
    
    if infer_type == "remove":
        image = decode_image(request.files.get("file").body)
        mask = Model().infer(image=image)
        for i in range(3): image[:, :, i] = image[:, :, i] & mask

        return JSONResponse(
            body={
                "statusText" : "Background Removal Successful",
                "version" : VERSION,
                "maskImageData" : encode_image_to_base64(image=mask),
                "bglessImageData" : encode_image_to_base64(image=image),
            },
            status=200,
        )
    
    elif infer_type == "replace":
        image_1 = decode_image(request.files.get("file_1").body)
        image_2 = decode_image(request.files.get("file_2").body)

        mask = Model().infer(image=image_1)
        mh, mw = mask.shape
        image_2 = preprocess_replace_bg_image(image_2, mw, mh)

        for i in range(3): 
            image_1[:, :, i] = image_1[:, :, i] & mask
            image_2[:, :, i] = image_2[:, :, i] & (255 - mask) 

        image_2 += image_1   

        return JSONResponse(
            body={
                "statusText" : "Background Replacement Successful",
                "version" : VERSION,
                "bgreplaceImageData" : encode_image_to_base64(image=image_2),
            },
            status=200,
        )
    
    else:
        return JSONResponse(
            body={
                "statusText" : "Invalid Infer Type",
                "version" : VERSION,
            },
            status=400,
        )

    
@app.post("/<infer_type:str>/li")
async def post_processing_li(request: Request, infer_type: str) -> JSONResponse:
    
    if infer_type == "remove":
        image = decode_image(request.files.get("file").body)
        mask = Model(lightweight=True).infer(image=image)
        for i in range(3): image[:, :, i] = image[:, :, i] & mask

        return JSONResponse(
            body={
                "statusText" : "Background Removal Successful",
                "version" : VERSION,
                "maskImageData" : encode_image_to_base64(image=mask),
                "bglessImageData" : encode_image_to_base64(image=image),
            },
            status=200,
        )
    
    elif infer_type == "replace":
        image_1 = decode_image(request.files.get("file_1").body)
        image_2 = decode_image(request.files.get("file_2").body)

        mask = Model(lightweight=True).infer(image=image_1)
        mh, mw = mask.shape
        image_2 = preprocess_replace_bg_image(image_2, mw, mh)

        for i in range(3): 
            image_1[:, :, i] = image_1[:, :, i] & mask
            image_2[:, :, i] = image_2[:, :, i] & (255 - mask) 

        image_2 += image_1   

        return JSONResponse(
            body={
                "statusText" : "Background Replacement Successful",
                "version" : VERSION,
                "bgreplaceImageData" : encode_image_to_base64(image=image_2),
            },
            status=200,
        )
    
    else:
        return JSONResponse(
            body={
                "statusText" : "Invalid Infer Type",
                "version" : VERSION,
            },
            status=400,
        )


if __name__ == "__main__":
    args_1: str = "--mode"
    args_2: str = "--workers"

    mode: str = "local"
    workers: int = 1

    if args_1 in sys.argv:
        mode = sys.argv[sys.argv.index(args_1) + 1]
    if args_2 in sys.argv:
        workers = int(sys.argv[sys.argv.index(args_2) + 1])

    if mode == "local":
        app.run(host="0.0.0.0", port=3030, dev=True, workers=workers)

    elif mode == "render":
        app.run(host="0.0.0.0", port=3030, single_process=True, access_log=True)

    elif mode == "prod":
        app.run(host="0.0.0.0", port=3030, dev=False, workers=workers, access_log=True)

    else:
        raise ValueError("Invalid Mode")