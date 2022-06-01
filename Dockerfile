FROM public.ecr.aws/lambda/python:3.8

RUN python3 -m pip install --upgrade pip

WORKDIR ${LAMBDA_TASK_ROOT}
COPY . ./

RUN pip3 install -r requirements.txt
RUN pip3 install awscli

CMD ["main.handler"]