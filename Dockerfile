FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nano \
    ruby-full \
    openjdk-11-jdk \
    wget \
    git \
    curl \
    gnupg-agent \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    systemd \
    rustc \
    tor \
    unzip

ARG DEBIAN_FRONTEND=noninteractive

RUN wget --quiet --output-document=android-sdk.zip https://dl.google.com/android/repository/commandlinetools-linux-6858069_latest.zip && \
    unzip -q android-sdk.zip -d android-sdk && \
    rm android-sdk.zip

ENV ANDROID_HOME=/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin

RUN yes | sdkmanager --licenses
RUN sdkmanager "platforms;android-30" "build-tools;30.0.2" "emulator"
# Genymotion Cloud
RUN pip3 install gmsaas
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN gmsaas config set android-sdk-path $ANDROID_HOME

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
CMD ["python3", "main.py"]
