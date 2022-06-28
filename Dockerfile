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
    libglib2.0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig \
    xvfb \
    libcurl4-openssl-dev

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY . ${FUNCTION_DIR}

# Install the runtime interface client
RUN pip install \
    --target ${FUNCTION_DIR} \
    awslambdaric

WORKDIR ${FUNCTION_DIR}

# Install requirements
RUN pip3 --no-cache-dir install -r requirements.txt

# Copy in the build image dependencies
# COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

COPY geckodriver /usr/local/bin/
COPY chromedriver /usr/local/bin/
# ADD https://objects.githubusercontent.com/github-production-release-asset-2e65be/84632322/975fea80-1573-11eb-8723-6279dc83226c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20220608%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220608T140116Z&X-Amz-Expires=300&X-Amz-Signature=e71144f2dfe40ddbf42fa281a701304c2ef33aff3502480282777538d8f52e68&X-Amz-SignedHeaders=host&actor_id=32714352&key_id=0&repo_id=84632322&response-content-disposition=attachment%3B%20filename%3Dstable-headless-chromium-amazonlinux-2.zip&response-content-type=application%2Foctet-stream /usr/local/bin/


ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD [ "main.handler" ]