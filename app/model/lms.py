import logging
from typing import Callable, TypeVar

import lmstudio as lms
from app.config.app_config import get_config

T = TypeVar("T")


def _create_client() -> lms.Client:
    return lms.Client(api_host=f'{get_config().lmstudio_api_host}:{get_config().lmstudio_api_port}')


_client = _create_client()


def call_with_reconnect(operation: Callable[[lms.Client], T]) -> T:
    """Run operation(client) against the shared LM Studio client.

    Reconnects and retries once if the client dropped, since a live
    handle (model/embedder) obtained from a disconnected client stays
    broken until a fresh Client is created.
    """
    global _client
    try:
        return operation(_client)
    except lms.LMStudioWebsocketError:
        logging.warning("LM Studio client disconnected, reconnecting...")
        _client = _create_client()
        return operation(_client)
