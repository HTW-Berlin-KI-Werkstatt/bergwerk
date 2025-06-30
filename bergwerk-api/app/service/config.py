from data import redis as data_redis
from model.configuration import ConfigItem

def get_configitem(item: str) -> ConfigItem:
    """
    Retrieve a specific configuration item from Redis.

    Parameters:
    - configitem: The key of the configuration item to retrieve.

    Returns:
    - A ConfigItem object containing the key and value.
    """

    return data_redis.get_configitem(item=item)

