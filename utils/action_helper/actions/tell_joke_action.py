from utils.action_utils import ActionUtils
import requests as rq


class TellJokeAction:
    def __init__(self) -> None:
        self.__url: str = 'https://v2.jokeapi.dev/joke/Any?lang=de&type=single'

    def __get_joke(self) -> str:
        response = rq.get(self.__url)
        joke = response.json()['joke']
        return joke

    def get_response(self, _1: str, main_str: str, error_str: str, _3: ActionUtils, _4: object) -> str:
        try:
            return main_str.format(joke=self.__get_joke())
        except (Exception,):
            return error_str
