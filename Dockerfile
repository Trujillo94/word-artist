# Define function directory
ARG FUNCTION_DIR="/function"

#FROM 082206641446.dkr.ecr.eu-west-3.amazonaws.com/winnow-video-converter-setup:latest
FROM python:3.10-slim

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    # libpoppler-cpp-dev \
    pkg-config \
    python-dev \
    g++ \
    make \
    cmake \
    # unzip \
    # ffmpeg \
    xvfb \
    libcurl4-openssl-dev

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy separately requirements.txt to function directory for Docker caching
COPY ./requirements.txt ${FUNCTION_DIR}

# Install requirements
RUN pip3 install --no-cache-dir --upgrade -r ${FUNCTION_DIR}/requirements.txt

# Install the runtime interface client
RUN pip install \
    --target ${FUNCTION_DIR} \
    awslambdaric

# Copy function code
COPY . ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
# COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

COPY geckodriver /usr/local/bin/
COPY chromedriver /usr/local/bin/

ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /

RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD [ "main.handler" ]