from typing import Dict
import re

from szurubooru import rest, config
from szurubooru.func import auth, file_uploads

import http
import json
import os

@rest.routes.post("/generate")
def genfile(
    ctx: rest.Context, _params: Dict[str, str] = {}
) -> rest.Response:
    auth.verify_privilege(ctx.user, "uploads:create")

    # Get the prompt from the request
    prompt = ctx.get_param_as_string("prompt")
    num_samples = 1 # hardcode to 1 for now TODO: change

    # Strip any negative rating queries if they exist
    # i.e. "-rating:safe,questionable,etc"
    # Do this by regexing for "-rating:\S+" and replacing with ""
    prompt = re.sub(r"-rating:\S+", "", prompt)

    # Generate the image
    # Get the worker url and port from the env variables
    worker_url = os.getenv("WORKER_URL")
    worker_port = os.getenv("WORKER_PORT")
    conn = http.client.HTTPConnection(worker_url, worker_port)
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
