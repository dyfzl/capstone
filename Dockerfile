# Base image
FROM python:3.11.4

# Install pytorch
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

# Set working directory
WORKDIR /fastapi

# Install python lib
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Copy files
COPY ./back/models /mindsearch/models
COPY ./back/main.py /mindsearch/
COPY ./back/packages /mindsearch/packages

CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8088"]