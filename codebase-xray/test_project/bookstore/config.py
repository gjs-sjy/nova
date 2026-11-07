import os

DEFAULTS = {"port": 8080, "tax_rate": 0.08}


def load_config():
    config = dict(DEFAULTS)
    config["port"] = int(get_setting("PORT", config["port"]))
    return config


def get_setting(name, default=None):
    return os.environ.get(name, default)


def legacy_config():
    # Old way of loading config. Nobody uses this anymore.
    return {"port": 80}
