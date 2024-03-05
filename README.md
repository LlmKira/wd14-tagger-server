# 🥽 wd14-tagger-server

This is the backend service implementation of wd14-tagger. It's an industrial-grade application, deployed with FastAPI
framework and hosted with PM2.

## 🔧 Config

Use the following commands to copy and edit the environment configuration file:

```shell
cp .env.exp .env
nano .env

```

## 🚀 Run

Here's how to run the server in your terminal:

```shell
pip install pdm
pdm install
pdm run python main.py

```

## PM2 🔄

These instructions help you start PM2 hosting and set it to automatically restart:

```shell
apt install npm
npm install pm2 -g
pip install pdm
pdm install
pm2 start pm2.json
pm2 stop pm2.json
pm2 restart pm2.json

```

## 📚 Docs

To view interface documentation and debug, visit the `/docs` page.

## Acknowledgement 🏅

- [FastAPI](https://fastapi.tiangolo.com/)
- [huggingface:SmilingWolf/wd-v1-4-tags](https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py)
