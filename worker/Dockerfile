FROM runpod/pytorch:latest as diffusers-worker

RUN pip3 install -U git+https://github.com/huggingface/diffusers.git
RUN pip3 install transformers scipy ftfy

# RUN pip install transformers gradio scipy ftfy "ipywidgets>=7,<8"
RUN pip3 install websocket-server flask

# Make sure that port is exposed for websockets
ARG PORT=9001
ENV PORT=${PORT}
EXPOSE ${PORT}

# Download fworker and run it
# wget https://raw.githubusercontent.com/VivaLaPanda/infinibooru/stable-diffusion/worker/fworker.py && python3 fworker.py
CMD ["/bin/bash", "-c", "wget https://raw.githubusercontent.com/VivaLaPanda/infinibooru/stable-diffusion/worker/fworker.py && python3 fworker.py"]