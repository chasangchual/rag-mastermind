import lmstudio as lms
from app.config.app_config import get_config

# lms.configure_default_client(get_config().lmstudio_api_url, get_config().lmstudio_api_key)

lms_default_client = lms.Client(api_host=f'{get_config().lmstudio_api_host}:{get_config().lmstudio_api_port}')