from io import BytesIO
from typing import Optional

from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File
from loguru import logger

from .infer import InferClient
from .infer.error import LoadError, FileSizeMismatchError, DownloadError
from .settings import InferSettingCurrent

app = FastAPI()


def verify_token(token):
    # TODO: Implement your token verification logic here
    return True


INFER_APP = InferClient(
    model_name=InferSettingCurrent.wd_model_name,
    model_dir=InferSettingCurrent.wd_model_dir,
)
logger.info(f"Infer app init success, model_path: {INFER_APP.model_path}")


@app.post("/upload")
async def upload(
    token: Optional[str] = None,
    file: UploadFile = File(...),
    general_threshold: Optional[float] = 0.35,
    character_threshold: Optional[float] = 0.85,
):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        image: Image = Image.open(BytesIO(await file.read()))
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
        return {
            "tag_result": tag_result,
            "origin_result": origin_result,
            "rating": rating,
            "character_res": character_res,
            "general_res": general_res,
        }
    except LoadError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    except DownloadError as e:
        # 下载模型文件失败
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Model download failed: {str(e)}")
    except FileSizeMismatchError as e:
        # 下载的模型文件大小不匹配
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="服务器内部错误...")
