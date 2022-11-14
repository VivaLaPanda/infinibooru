FROM runpod/stack:latest as diffusers-worker

# Set /workspace as the pwd
WORKDIR /workspace

# Get https://github.com/VivaLaPanda/naifu/archive/refs/heads/master.zip
# and place the file in ./naifu
ADD https://github.com/VivaLaPanda/naifu/archive/refs/heads/master.tar.gz /tmp/naifu.tar.gz
RUN tar -xJf /tmp/naifu.tar.gz-C /tmp && \
    mv /tmp/naifu-master /workspace/naifu \
    rm /tmp/naifu.zip

# Get http://143.110.234.53/models/naifumodels.tar.gz and put it in ./naifu/models
ADD http://143.110.234.53/models/naifumodels.tar.gz /tmp/naifumodels.tar.gz
RUN tar -xJf /tmp/naifumodels.tar.gz -C /tmp && \
    mv /tmp/naifumodels /workspace/naifu/models \
    rm /tmp/naifumodels.tar.gz

# Run the setup script (/workspace/naifu/setup.sh)
RUN /workspace/naifu/setup.sh

RUN /workspace/naufu/run.sh