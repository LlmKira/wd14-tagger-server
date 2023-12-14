import pathlib

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
    download(url=file_url, folder=file_dir, filename=file_name)
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
