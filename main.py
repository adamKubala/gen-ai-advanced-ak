from config import get_config, get_tasks
from utils.logger import get_logger

logger = get_logger(__name__)

cfg = get_config()
print(cfg.log_level)
print(cfg.api_key)                    # **********  (zamaskowany)
print(cfg.api_key.get_secret_value()) # prawdziwa wartość

tasks = get_tasks()
print(tasks.task("precise").temperature, tasks.task("precise").models)
