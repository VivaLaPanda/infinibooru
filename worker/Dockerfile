FROM runpod/pytorch:latest as diffusers-worker

RUN pip3 install -U git+https://github.com/huggingface/diffusers.git
RUN pip3 install transformers scipy ftfy

# RUN pip install transformers gradio scipy ftfy "ipywidgets>=7,<8"
RUN pip3 install websocket-server

# Set the cache directory based on .env
ENV CACHE_DIR=/tmp/waifu-diffusion

# Make sure the cache dir exists
RUN mkdir -p $CACHE_DIR
# Mount the cache directory to /tmp/models
VOLUME $CACHE_DIR
# Make sure we can write to the cache directory
RUN chmod -R 777 $CACHE_DIR

# Make sure that port is exposed for websockets
EXPOSE $port

# Start the worker.py websocket server
RUN wget https://gist.github.com/VivaLaPanda/c504c2aea9c137638b723aef86bd88a4/raw/347c2796484737053c677ab5b7b024295aa4c054/fworker.py

# Make the worker.py the entrypoint
ENTRYPOINT ["python3 fworker.py"]