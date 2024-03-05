FROM python:3.9-slim
WORKDIR /usr/src/app
COPY . .
RUN cp .env.exp .env
RUN sed -i 's|SERVER_HOST=127.0.0.1|SERVER_HOST=0.0.0.0|' .env
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN pip install pdm
RUN pdm install
CMD ["pdm", "run", "python3", "main.py"]