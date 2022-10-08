import base64
from io import BytesIO
import json
import os
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from flask import Flask, request

# Get port from ENV
app = Flask(__name__)

# Function to set up the model pipe
def setup_model():
    # Get model_id from env
    model_id = os.environ.get('MODEL_ID', 'hakurei/waifu-diffusion')
    cache_dir = os.environ.get('CACHE_DIR', '/tmp/models')
    device = "cuda"

    # Load model
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32, cache_dir=cache_dir)
    pipe = pipe.to(device)

    # Disable safety checker
    def dummy(images, **kwargs):
        return images, False
    pipe.safety_checker = dummy

    return pipe


# Store pipe as a global variable
pipe = setup_model()

@app.route('/generate_image', methods=['POST'])
def generate_image():
    # Parse the JSON message
    message = request.get_json()
    print("Received message: %s" % message)

    # Extract the prompt from the message
    prompt = message['prompt']
    num_samples = message['num_samples']

    # If num_samples is not specified, default to 1
    if num_samples is None:
        num_samples = 1
    
    # Generate the image
    # TODO: Add a timeout
    with autocast("cuda"):
        images = pipe([prompt] * num_samples, guidance_scale=7.5, )["sample"]
    
    # Images is a list of PIL images. Respond with am image binary instead
    image = images[0]
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    # image_string = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Send the images back to the client
    return buffered.getvalue()

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 9001))
    print("Starting server on port %d" % PORT)
    app.run(host='0.0.0.0', port=PORT)