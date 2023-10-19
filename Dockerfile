FROM public.ecr.aws/lambda/python:3.9

# app directory
COPY ./app ${LAMBDA_TASK_ROOT}

# copy requirements.txt to the docker image 
COPY requirements.txt .

# Install dependencies for API
RUN pip3 install -r requirements.txt - target "${LAMBDA_TASK_ROOT}" -U - no-cache-dir

# Expose port
EXPOSE 8080

# Set CMD to Magum app handler
CMD [ "app.handler" ]