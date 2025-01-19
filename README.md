# 🥽 wd-tagger-server

This is the backend service implementation of [wd-tagger](https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags). It's
an industrial-grade application, deployed with FastAPI
framework and hosted with PM2.

## Quick View

```shell
curl -X 'POST' \
  'http://127.0.0.1:5010/upload?general_threshold=0.35&character_threshold=0.85' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@the_image_for_upload.png;type=image/png'
```

**All Model You Can Use Here**: [app/values.py](https://github.com/LlmKira/wd14-tagger-server/blob/main/app/values.py)

## 🔧 Config

Use the following commands to copy and edit the environment configuration file:

```shell
cp .env.exp .env
nano .env

```

- Here's how to run the server in your terminal:

```shell
pip install pdm
pdm install
pdm run python main.py

```

- To run in Docker:

```shell
docker build --rm -t wd14taggerserver:latest "."
docker run -d -p 5010:5010 wd14taggerserver:latest
```

## Hosting 🚀

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

### Return Example

```json5
{
  "tag_result": "1girl, twintails, hat, long hair, detached sleeves, aqua hair, cigarette, old, skull, smoking, necktie, beard, old man, witch hat, sitting, skirt, very long hair, facial hair, 1boy, bottle, wizard, smoke, table, aqua eyes, holding",
  "sorted_general_strings": "1girl, twintails, hat, long hair, detached sleeves, aqua hair, cigarette, old, skull, smoking, necktie, beard, old man, witch hat, sitting, skirt, very long hair, facial hair, 1boy, bottle, wizard, smoke, table, aqua eyes, holding",
  "rating": {
    "general": 0.43704715371131897,
    "sensitive": 0.5824227333068848,
    "questionable": 0.0014189481735229492,
    "explicit": 0.0003159642219543457
  },
  "character_res": {
    "hatsune miku": 0.9932807683944702
  },
  "general_res": {
    "1girl": 0.9735698699951172,
    "long hair": 0.9188452959060669,
    "skirt": 0.6999160647392273,
    "1boy": 0.5983260869979858,
    "hat": 0.9251259565353394,
    "holding": 0.4740619659423828,
    "very long hair": 0.6469190716743469,
    "sitting": 0.7056105136871338,
    "twintails": 0.9444608688354492,
    "necktie": 0.8174249529838562,
    "detached sleeves": 0.9134520888328552,
    "aqua eyes": 0.5212169885635376,
    "aqua hair": 0.8804699182510376,
    "facial hair": 0.6368286609649658,
    "witch hat": 0.7379000186920166,
    "table": 0.5278599858283997,
    "bottle": 0.5711551308631897,
    "beard": 0.7684704661369324,
    "smoke": 0.5494353771209717,
    "cigarette": 0.8674004077911377,
    "skull": 0.8451370000839233,
    "smoking": 0.8203994631767273,
    "old": 0.8643935322761536,
    "old man": 0.7388820052146912,
    "wizard": 0.5636041164398193
  }
}
```

Python [sdk.py](https://github.com/LlmKira/wd14-tagger-server/blob/main/sdk.py)

## Acknowledgement 🏅

- [FastAPI](https://fastapi.tiangolo.com/)
- [huggingface:SmilingWolf/wd-v1-4-tags](https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py)
