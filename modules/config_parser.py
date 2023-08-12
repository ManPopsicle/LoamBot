import os
from typing import List, Dict

import confuse


def _extract_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ["true", "yes", "1", "t"]:
        return True
    elif value.lower() in ["false", "no", "0", "f"]:
        return False
    else:
        raise ValueError("Not a boolean: {}".format(value))


class ConfigSection:
    def __init__(self, section_key: str, data, parent_key: str = None, pull_from_env: bool = True):
        self.section_key = section_key
        self.data = data
        self.pull_from_env = pull_from_env
        try:
            self.data = data[self.section_key]
        except confuse.NotFoundError:
            pass
        self._parent_key = parent_key

    @property
    def full_key(self):
        if self._parent_key is None:
            return self.section_key
        return f"{self._parent_key}_{self.section_key}".upper()

    def _get_value(self, key: str, default=None, env_name_override: str = None):
        if self.pull_from_env:
            env_name = env_name_override or self.full_key
            return os.getenv(env_name, default)
        try:
            return self.data[key].get()
        except confuse.NotFoundError:
            return default

    def _get_subsection(self, key: str, default=None):
        try:
            return ConfigSection(section_key=key, parent_key=self.full_key, data=self.data,
                                 pull_from_env=self.pull_from_env)
        except confuse.NotFoundError:
            return default


class LibrariesConfig(ConfigSection):
    def __init__(self, data, pull_from_env: bool = True):
        super().__init__(section_key="Libraries", data=data, pull_from_env=pull_from_env)


    @property
    def movie_library(self) -> List[str]:
        data = self._get_value(key="Movies", default=[],
                                                  env_name_override="MOVIES_LIBRARY")
        if isinstance(data, str):
            return data.split(",")  # Dealing with a comma separated list in an environment variable
        return data

    @property
    def shows_library(self) -> List[str]:
        data = self._get_value(key="Shows", default=[],
                                                  env_name_override="SHOWS_LIBRARY")
        if isinstance(data, str):
            return data.split(",")  # Dealing with a comma separated list in an environment variable
        return data

class VlcConfig(ConfigSection):
    def __init__(self, data, pull_from_env: bool = True):
        super().__init__(section_key="VLC", data=data, pull_from_env=pull_from_env)

    @property
    def password(self) -> str:
        return self._get_value(key="Password", env_name_override="VLC_PASSWORD")

    @property
    def host(self) -> str:
        return self._get_value(key="Host", env_name_override="VLC_HOST")

    @property
    def port(self) -> str:
        return self._get_value(key="Port", env_name_override="VLC_PORT")
    
    @property
    def shuffle(self) -> bool:
        return self._get_value(key="Shuffle", env_name_override="VLC_SHUFFLE")


class DiscordConfig(ConfigSection):
    def __init__(self, data, pull_from_env: bool = True):
        super().__init__(section_key="Discord", data=data, pull_from_env=pull_from_env)

    @property
    def bot_token(self) -> str:
        return self._get_value(key="BotToken", env_name_override="PR_DISCORD_BOT_TOKEN")

    @property
    def bot_prefix(self) -> str:
        return self._get_value(key="BotPrefix", env_name_override="PR_DISCORD_BOT_PREFIX")

    @property
    def owner_id(self) -> str:
        return self._get_value(key="OwnerID", env_name_override="PR_DISCORD_OWNER_ID")



class Config:
    def __init__(self, app_name: str, config_path: str, fallback_to_env: bool = True):
        self.config = confuse.Configuration(app_name)
        self.pull_from_env = False
        # noinspection PyBroadException
        try:
            self.config.set_file(filename=config_path)
        except Exception:  # pylint: disable=broad-except # not sure what confuse will throw
            if not fallback_to_env:
                raise FileNotFoundError(f"Config file not found: {config_path}")
            self.pull_from_env = True

        self.vlc = VlcConfig(self.config, self.pull_from_env)
        self.discord = DiscordConfig(self.config, self.pull_from_env)
        self.libraries = LibrariesConfig(self.config, self.pull_from_env)
        try:
            self.log_level = self.config['logLevel'].get() or "INFO"
        except confuse.NotFoundError:
            self.log_level = "WARN"  # will only be WARN when pulling config from env (i.e. Docker)
