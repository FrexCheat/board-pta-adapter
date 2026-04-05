from collections.abc import Callable
from typing import TypeVar

from loguru import logger

from adapter.config import load_config
from adapter.models.config import Config
from common.utils.storage import OutputStorage

AdapterT = TypeVar("AdapterT")


def build_runtime(
    adapter_factory: Callable[[Config], AdapterT],
    output_dir_getter: Callable[[Config], str],
) -> tuple[Config, AdapterT, OutputStorage]:
    try:
        config = load_config()
        adapter = adapter_factory(config)
        storage = OutputStorage(output_dir_getter(config))
    except Exception:
        logger.exception("===> failed to initialize runtime.")
        raise

    return config, adapter, storage
