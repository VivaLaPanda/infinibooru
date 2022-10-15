import random
from typing import Dict
import re

from szurubooru import rest
from szurubooru.func import auth, file_uploads

import http
import json
import os
import base64
import sys


multichar_regex = r"[2-6]\+*(boys)*(girls)*"

def negative_prompt(rawprompt):
    prompt = "lowres, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

    if "futanari" not in prompt:
        prompt = "bad anatomy, " + prompt

    if "1boy" in rawprompt:
        prompt = "breasts, large_breasts, pussy, " + prompt
    
    if "loli" in rawprompt and "oppai" not in rawprompt:
        prompt = "large_breasts, medium_breasts, mature_woman, " + prompt
    
    if "shota" in rawprompt:
        prompt = "mature_male, stubble, muscular_male, " + prompt
    
    if "1girl" in rawprompt and "1boy" in rawprompt:
        prompt = "solo, " + prompt
    
    if "boy" not in rawprompt and "futanari" not in rawprompt:
        prompt = "penis, " + prompt

    if "solo" in rawprompt:
        if "1girl" in rawprompt:
            prompt = "1boy, " + prompt
        if "1boy" in rawprompt:
            prompt = "1girl, " + prompt
    
    # match n-many boys or girls
    if re.search(multichar_regex, rawprompt):
        prompt = "solo, " + prompt
    
    return prompt

def format_prompt(rawprompt):
    # Strip any negative rating queries if they exist
    # i.e. "-rating:safe,questionable,etc"
    # Do this by regexing for "-rating:\S+" and replacing with ""
    prompt = re.sub(r"-rating:\S+", "", rawprompt)

    # Remove underscores from prompt
    prompt = prompt.replace("_", " ")

    # Append "masterpiece, best quality, " to prompt
    prompt = "masterpiece, best quality, " + prompt

    if "explicit" in rawprompt:
        prompt = "NSFW, " + prompt
    
    if "loli" in rawprompt or "shota" in rawprompt:
        prompt += ", child"

    return prompt

def guessSize(prompt):
    long = 768
    medium = 640
    short = 512
    # Guess size of image based on prompt
    # set the default
    size = {
        "height": long,
        "width": short
    }

    # Check if prompt contains terms that indicate whether they want
    # portrait, landscape or square
    if "landscape" in prompt:
        size = {
            "height": short,
            "width": long
        }

    if re.search(multichar_regex, prompt):
        # randomly chose portrait or landscape
        if random.randint(0,1) == 1:
            size = {
                "height": short,
                "width": long
            }

    
    if "square" in prompt:
        size = {
            "height": medium,
            "width": medium
        }
    
    if "wide_image" in prompt or "wallpaper" in prompt:
        size = {
            "height": short,
            "width": 1024
        }

    return size


@rest.routes.post("/generate")
def genfile(
    ctx: rest.Context, _params: Dict[str, str] = {}
) -> rest.Response:
    auth.verify_privilege(ctx.user, "uploads:create")

    # Get the prompt from the request
    prompt = ctx.get_param_as_string("prompt")
    num_samples = 1 # hardcode to 1 for now TODO: change

    dimm = guessSize(prompt)
    prompt = format_prompt(prompt)
    neg_prompt = negative_prompt(prompt)

    # Generate the image
    # Get the worker url and port from the env variables
    worker_url = os.getenv("WORKER_URL")
    worker_port = os.getenv("WORKER_PORT")
    conn = http.client.HTTPConnection(worker_url, worker_port)
#     curl 'http://81.82.209.54:10002/generate-stream' \
#   -H 'Connection: keep-alive' \
#   -H 'Content-Type: application/json' \
#   --data-raw '{"prompt":"masterpiece, best quality, 1girl, daiwa scarlet (umamusume), umamusume, tiara, horse ears, horse girl, horse tail, jewelry, large breasts, adjusting dress, animal ears, bangs, bare arms, blush, bracelet, breasts, brown hair, choker, cleavage, covered navel, cowboy shot, dress, hair between eyes, hair intakes, hair over shoulder, long hair, nail polish, necklace, red choker, red dress, red eyes, red nails, skindentation, solo, tail, thighhighs, thighs, very long hair","width":512,"height":768,"scale":12,"sampler":"k_euler_ancestral","steps":28,"seed":480161451,"n_samples":1,"ucPreset":0,"uc":"lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"}' \
#   --insecure

    payload = json.dumps({
        "prompt": prompt,
        "n_samples": num_samples,
        "sampler": "k_euler_ancestral",
        "scale": 12,
        "steps": 30,
        "uc": neg_prompt,
        "ucPreset": 0,
        "width": dimm["width"],
        "height": dimm["height"]
    })
    print(payload, file=sys.stderr)

    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/generate-stream", payload, headers)
    # Response is an eventstream
    # Get the first "newImage" event and get the data content
    event = {}
    with conn.getresponse() as response:
        # check resp code is ok
        if not response.status == 200:
            print(response.read()[:200], file=sys.stderr)
            raise Exception("Error generating image")

        while not response.closed:
            for line in response:
                line = line.decode('UTF-8')
                # print line to stderr
                if line == '\r\n':
                    # End of event.
                    response.close()
                    break
                elif line.startswith(':'):
                    # Comment, ignore.
                    pass
                else:
                    # Data line.
                    try:
                        key, value = line.split(':', 1)
                        value = value.strip()
                        if key == 'data':
                            event[key] = value
                    except:
                        # we're done, close the resp
                        response.close()
                        break

    # get the newImage event
    base64Image = event["data"]
    # Decode the base64 image into binary byes
    binaryImage = base64.b64decode(base64Image)

    token = file_uploads.save(binaryImage)
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
