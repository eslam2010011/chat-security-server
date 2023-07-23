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
    unzip \
    openssh-server

ARG DEBIAN_FRONTEND=noninteractive


# Ssh
RUN echo 'root:password' | chpasswd
RUN ssh-keygen -A

# Change SSH port to 2222
RUN sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

EXPOSE 2222 


# Android
#ENV ANDROID_COMMAND_LINE_TOOLS_FILENAME commandlinetools-linux-7583922_latest.zip
#ENV ANDROID_API_LEVELS                  android-33
#ENV ANDROID_BUILD_TOOLS_VERSION         32.0.0
#
#ENV ANDROID_HOME /usr/local/android-sdk-linux
#ENV PATH         ${PATH}:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/cmdline-tools/bin
#
#RUN cd /usr/local/
#RUN wget -q "https://dl.google.com/android/repository/${ANDROID_COMMAND_LINE_TOOLS_FILENAME}"
#RUN unzip ${ANDROID_COMMAND_LINE_TOOLS_FILENAME} -d /usr/local/android-sdk-linux
#RUN rm ${ANDROID_COMMAND_LINE_TOOLS_FILENAME}
#
#RUN yes | sdkmanager --update --sdk_root="${ANDROID_HOME}"
#RUN yes | sdkmanager platform-tools --sdk_root="${ANDROID_HOME}"
#
#RUN yes | sdkmanager --sdk_root="${ANDROID_HOME}" "platforms;${ANDROID_API_LEVELS}" "build-tools;${ANDROID_BUILD_TOOLS_VERSION}" "extras;google;m2repository" "extras;android;m2repository" "extras;google;google_play_services"
#
#RUN yes | sdkmanager --licenses --sdk_root="${ANDROID_HOME}"
#



# Genymotion Cloud
#RUN pip3 install gmsaas
#RUN gmsaas config set android-sdk-path ${ANDROID_HOME}
#


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
CMD ["/usr/sbin/sshd", "-D", "-p", "2222"]
CMD ["python3", "main.py"]
