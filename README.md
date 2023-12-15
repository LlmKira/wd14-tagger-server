# wd14-tagger-server

wd14-tagger 的后端服务实现。工业级应用，使用 FastAPI 框架，使用 PM2 托管。

## Config

```shell
cp .env.exp .env
nano .env

```

## Run

在终端中运行

```shell
pip install pdm
pdm install
pdm run python main.py

```

## PM2

启动 pm2 托管，自动重启

```shell
apt install npm
npm install pm2 -g
pip install pdm
pdm install
pm2 start pm2.json
pm2 stop pm2.json
pm2 restart pm2.json

```

## Docs

访问 `/docs` 页面查看接口文档并调试

## Acknowledgement

- [FastAPI](https://fastapi.tiangolo.com/)
- [huggingface:SmilingWolf/wd-v1-4-tags](https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py)
