import pathlib
from urllib.error import URLError

from loguru import logger
from robust_downloader import download


async def download_file(file_name: str, file_url: str, file_dir: str):
    """
    Download file from url
    :param file_name: File name
    :param file_url: File url
    :param file_dir: The directory to store the file
    :return: None
    :raises: DownloadError, FileSizeMismatchError
    """
    if download(url=file_url, folder=file_dir, filename=file_name, timeout=20):
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
    ab_path = pathlib.Path(file_dir).joinpath(f"{model_name}.onnx").absolute()
    try:
        await download_file(f"{model_name}.onnx", model_url, file_dir=file_dir)
    except URLError:
        if pathlib.Path(file_dir).joinpath(f"{model_name}.onnx").exists():
            logger.warning(
                f"Model {model_name} download failed, but file exists, skip download"
            )
            return str(ab_path)
        raise URLError(f"Model {model_name} download failed")
    except Exception as e:
        raise e
    else:
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
    ab_path = pathlib.Path(file_dir).joinpath(f"{model_name}.csv").absolute()
    try:
        await download_file(f"{model_name}.csv", csv_url, file_dir=file_dir)
    except URLError:
        if pathlib.Path(file_dir).joinpath(f"{model_name}.csv").exists():
            logger.warning(
                f"Tagger CSV {model_name} download failed, but file exists, skip download"
            )
            return str(ab_path)
        raise URLError(f"Model {model_name} download failed")
    except Exception as e:
        raise e
    else:
        logger.info(f"Tagger CSV {model_name} downloaded at {ab_path}")
    return str(ab_path)
