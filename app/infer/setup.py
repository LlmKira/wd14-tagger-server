import os
import pathlib

import httpx
from loguru import logger
from rich.progress import Progress

from .error import DownloadError, FileSizeMismatchError


async def download_file(file_name: str, file_url: str, file_dir: str):
    """
    Download file from url
    :param file_name: File name
    :param file_url: File url
    :param file_dir: The directory to store the file
    :return: None
    :raises: DownloadError, FileSizeMismatchError
    """
    file_dir_obj = pathlib.Path(file_dir)
    file_path = file_dir_obj.joinpath(file_name)
    if file_path.exists():
        existing_size = os.path.getsize(file_path)
        logger.warning(
            f"File {file_name} already exists with size {existing_size} bytes"
        )
    logger.info(
        f"Start download file {file_name} from {file_url} to {file_path.absolute()}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.head(file_url)
        if resp.status_code == 302:
            file_url = resp.headers["Location"]
            logger.info(f"Redirected to {file_url}, start download again")
            resp = await client.get(
                file_url
            )  # Make a new GET request to the redirected URL
        elif resp.status_code != 200:
            raise DownloadError(
                f"Download file {file_name} from {file_url} failed, status code: {resp.status_code}"
            )
        total_size = int(resp.headers.get("content-length", 0))
        if file_path.exists():
            existing_size = os.path.getsize(file_path)
            if existing_size == total_size:
                logger.info(f"File {file_name} already downloaded with correct size")
                return
            else:
                logger.warning(
                    f"File {file_name} already exists with size {existing_size} bytes, re-download"
                )
        resp = await client.get(file_url)
        progress = Progress()
        task_id = progress.add_task("[cyan]Downloading...", total=total_size)
        with progress:
            with open(file_path, "wb") as f:
                while not progress.finished:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))

    downloaded_size = os.path.getsize(file_path)
    if downloaded_size != total_size:
        raise FileSizeMismatchError(
            f"Expected {total_size} bytes, but got {downloaded_size} bytes"
        )
    logger.success(f"Download file {file_name} from {file_url} success")


async def download_model(model_name: str, file_dir: str = "models") -> str:
    """
    Download model from url
    :param model_name: Model name
    :param file_dir: The directory to store the file
    :return: None
    """
    # Get Current Path / Create models folder
    pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)
    # Download
    model_url = (
        f"https://huggingface.co/SmilingWolf/{model_name}/resolve/main/model.onnx"
    )
    await download_file(f"{model_name}.onnx", model_url, file_dir=file_dir)
    ab_path = pathlib.Path(file_dir).joinpath(f"{model_name}.onnx").absolute()
    logger.info(f"Model {model_name} downloaded at {ab_path}")
    return str(ab_path)


async def download_csv(model_name: str, file_dir: str = "models") -> str:
    """
    Download csv from url
    :param model_name: Model name
    :param file_dir: The directory to store the file
    :return: None
    """
    # Get Current Path / Create models folder
    pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)
    # Download
    csv_url = f"https://huggingface.co/SmilingWolf/{model_name}/resolve/main/selected_tags.csv"
    await download_file(f"{model_name}.csv", csv_url, file_dir=file_dir)
    ab_path = pathlib.Path(file_dir).joinpath(f"{model_name}.csv").absolute()
    logger.info(f"Tagger CSV {model_name} downloaded at {ab_path}")
    return str(ab_path)
