import json


class ConfigManager:
    __instance = None
    __config = None
    __filename = None

    def __new__(cls, filename):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__filename = filename
            cls.__instance.__load_config()
        return cls.__instance

    def __load_config(self) -> None:
        with open(self.__filename, "r") as file:
            self.__config = json.load(file)

    def __save_config(self) -> None:
        with open(self.__filename, "w") as file:
            json.dump(self.__config, file)

    def get_config(self, keyword: str) -> dict:
        return self.__config[keyword]

    def set_config(self, keyword: str, value) -> None:
        self.__config[keyword] = value
        self.__save_config()


