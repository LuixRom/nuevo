FROM public.ecr.aws/lambda/python:3.12

# Instala dependencias de sistema
RUN yum install -y wget unzip && \
    pip install --upgrade pip

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Instalar browsers para Playwright
RUN playwright install --with-deps

# Copiar código
COPY app/ ${LAMBDA_TASK_ROOT}/

# Setear handler
CMD ["main.lambda_handler"]
