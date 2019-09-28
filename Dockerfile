FROM debian:stable-slim

EXPOSE 8888

# Set UTF-8 locales
ENV LANG=C.UTF-8

# Create User
ARG USER="clips"
ARG HOME="/home/clips"
RUN useradd --create-home --home-dir $HOME $USER

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y \
        gcc \
        make \
        wget \
        unzip \
        python3 \
        python3-pip \
        python3-cffi

# Install CLIPSPy from sources
ENV PYTHON python3
RUN wget https://github.com/noxdafox/clipspy/archive/master.zip && \
        unzip master.zip && \
        cd clipspy-master && \
        make && \
        make install && \
        cd .. && \
        rm -fr master.zip clipspy-master

# Install Python packages
RUN pip3 install iclips jupyter

# Switch to CLIPS User
USER $USER
WORKDIR $HOME

CMD ["jupyter", "notebook", "--no-browser", "--ip", "0.0.0.0", "--port=8888"]
