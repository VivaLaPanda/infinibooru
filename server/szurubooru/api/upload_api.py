from typing import Dict

from szurubooru import rest
from szurubooru.func import auth, file_uploads

import http.client
import json


@rest.routes.post("/generate")
def genfile(
    ctx: rest.Context, _params: Dict[str, str] = {}
) -> rest.Response:
    auth.verify_privilege(ctx.user, "uploads:create")

    # Lock so that we're only ever generating one image at a time
    

    # Get the prompt from the request
    prompt = ctx.get_param_as_string("prompt")
    num_samples = 1 # hardcode to 1 for now TODO: change
    # Generate the image
    conn = http.client.HTTPConnection("24.65.87.40", 40025)
    payload = json.dumps({
        "prompt": prompt,
        "num_samples": num_samples
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/generate_image", payload, headers)
    res = conn.getresponse()
    data = res.read()

    token = file_uploads.save(data)
    return {"token": token}

@rest.routes.post("/uploads/?")
def create_temporary_file(
    ctx: rest.Context, _params: Dict[str, str] = {}
) -> rest.Response:
    auth.verify_privilege(ctx.user, "uploads:create")
    content = ctx.get_file(
        "content",
        allow_tokens=False,
        use_video_downloader=auth.has_privilege(
            ctx.user, "uploads:use_downloader"
        ),
    )
    token = file_uploads.save(content)
    return {"token": token}
