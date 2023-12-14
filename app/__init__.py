# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午7:43
# @Author  : sudoskys
# @File    : __init__.py
# @Software: PyCharm
from io import BytesIO

from PIL import Image
from loguru import logger
from sanic import Sanic, response
from sanic.exceptions import Unauthorized, ServerError
from sanic.request import Request
from sanic.response import HTTPResponse

from .infer import InferClient
from .infer.error import LoadError, FileSizeMismatchError, DownloadError
from .settings import InferSettingCurrent

app = Sanic(__name__)


def verify_token(token):
    # TODO: Implement your token verification logic here
    return True


INFER_APP = InferClient(
    model_name=InferSettingCurrent.wd_model_name,
    model_dir=InferSettingCurrent.wd_model_dir,
)
logger.info(f"Infer app init success, model_path: {INFER_APP.model_path}")


@app.route("/upload", methods=["POST"])
async def upload(request: Request) -> HTTPResponse:
    token: str = request.token
    if not verify_token(token):
        raise Unauthorized("Invalid token")

    if not request.files:
        raise ServerError("No file provided")

    file = request.files.get("file")
    if not file:
        raise ServerError("No file provided")

    general_threshold: float = float(request.args.get("general_threshold", 0.35))
    character_threshold: float = float(request.args.get("character_threshold", 0.85))

    try:
        image: Image = Image.open(BytesIO(file.body))
        (
            tag_result,
            origin_result,
            rating,
            character_res,
            general_res,
        ) = await INFER_APP.infer(
            image=image,
            general_threshold=general_threshold,
            character_threshold=character_threshold,
        )
        return response.json(
            {
                "tag_result": tag_result,
                "origin_result": origin_result,
                "rating": rating,
                "character_res": character_res,
                "general_res": general_res,
            }
        )
    except LoadError as e:
        logger.error(e)
        raise ServerError(str(e))
    except DownloadError as e:
        # 下载模型文件失败
        logger.error(e)
        raise ServerError(f"Model download failed: {str(e)}")
    except FileSizeMismatchError as e:
        # 下载的模型文件大小不匹配
        logger.error(e)
        raise ServerError(str(e))
    except Exception as e:
        logger.error(e)
        raise ServerError("服务器内部错误...")
