from typing import Dict
import logging
import requests
import re

from szurubooru import rest
from szurubooru.func import auth, file_uploads

import replicate
logger = logging.getLogger(__name__)

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
    model = replicate.models.get("cjwbw/waifu-diffusion")
    output = model.predict(prompt=prompt)[0] # We only allow generating one, so just 0-index

    # Fix faces
    # TODO: can't find a good model for anime images

    # The output is a url to the image on replicate e.g. 'https://replicate.com/api/models/cjwbw/waifu-diffusion/files/ba595ffd-8d93-4936-875b-caf8f4d09688/out-0.png'
    # Download it using requests
    r = requests.get(output, allow_redirects=True)
    # Get the bytes from the response as "data"
    data = r.content

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
