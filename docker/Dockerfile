FROM nvidia/cudagl:11.3.1-base-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    git \
    cmake \
    curl \
    g++ \
    make \
    vim \
    wget \
    cuda-command-line-tools-11-3 \
    libegl1-mesa-dev \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libglfw3-dev \
    libx11-dev \
    libxcursor-dev \
    libxrandr-dev \
    libxi-dev \
    libxxf86vm-dev \
    libxinerama-dev \
    libsm6 \
    ca-certificates \
    python3.8 \
    python3.8-distutils \
    python3.8-dev \
    python3-pip \
    python3-apt \
    && rm -rf /var/lib/apt/lists/*

RUN update-ca-certificates

RUN ln -sf /usr/bin/python3.8 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

RUN pip install --upgrade pip

RUN pip install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio==0.10.0+cu113 \
    -f https://download.pytorch.org/whl/cu113/torch_stable.html --no-cache-dir

RUN git clone https://github.com/embodied-agent-interface/iGibson.git /opt/iGibson --recursive

RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install -y git-lfs && \
    git lfs install

WORKDIR /opt/iGibson
RUN pip install --no-cache-dir -e .

RUN yes | python -m igibson.utils.assets_utils --download_assets && rm -rf /tmp/*
RUN yes | python -m igibson.utils.assets_utils --download_ig_dataset && rm -rf /tmp/*
RUN python -m igibson.utils.assets_utils --download_ig_key && rm -rf /tmp/*

RUN pip install eai-eval==1.0.3
