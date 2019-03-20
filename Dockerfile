FROM debian:stable-slim

EXPOSE 8888

# Set UTF-8 locales
ENV LANG=C.UTF-8

# Create User
ARG USER="clips"
ARG HOME="/home/clips"
RUN useradd --create-home --home-dir $HOME $USER

# Install Debian packages
RUN echo "APT::Default-Release \"stable\";" >> /etc/apt/apt.conf
RUN echo "deb http://ftp.se.debian.org/debian/ unstable main" >> /etc/apt/sources.list

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
        python3-cffi \
        libclips/unstable \
        libclips-dev/unstable

# Install Python packages
RUN pip3 install iclips jupyter

# Switch to CLIPS User
USER $USER
WORKDIR $HOME

CMD ["jupyter", "notebook", "--no-browser", "--ip", "0.0.0.0", "--port=8888"]
