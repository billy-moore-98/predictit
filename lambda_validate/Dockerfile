FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

COPY ./lambda_validate/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt --target .

COPY ./lambda_validate/lambda_function.py ./
COPY ./src ./src

CMD ["lambda_function.lambda_handler"]