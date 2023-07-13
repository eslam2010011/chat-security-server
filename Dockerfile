FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nano \
    ruby-full \
    openjdk-8-jdk \
    wget \
    git \
    curl \
    gnupg-agent \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    systemd \
    rustc \
    tor

ARG DEBIAN_FRONTEND=noninteractive

# Install Docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io


# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs

# Install Go
RUN apt-get update && apt-get install -y wget
RUN wget https://go.dev/dl/go1.20.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.20.5.linux-amd64.tar.gz && \
    rm go1.20.5.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"


ENV GOPATH="/app/go"
ENV PATH="${PATH}:${GOPATH}/bin"

RUN echo "export PATH=\$PATH:${GOPATH}/bin" >> ~/.bashrc && \
    echo "export PATH=\$PATH:${GOPATH}/bin" >> ~/.profile


RUN sed -i 's/^#\s*\(deb.*universe\)$/\1/g' /etc/apt/sources.list
RUN apt-get update && apt-get install -y systemd-sysv

WORKDIR /app

RUN python3.10 -m venv venv
ENV PATH="/app/venv/bin:${PATH}"

COPY requirements.txt /app
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV SECRET_KEY=""

CMD ["/lib/systemd/systemd"]

#CMD ["service tor start"]

CMD ["python3", "main.py"]

