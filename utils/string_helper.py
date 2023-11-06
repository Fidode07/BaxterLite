import gensim.downloader as gensim_api
import numpy as np
import nltk
from nltk import word_tokenize
from dataclasses import dataclass

nltk.download('punkt')


@dataclass
class Model:
    def __init__(self, name: str, size: int, dimensions: int) -> None:
        self.name: str = name
        self.size: int = size
        self.dimensions: int = dimensions


class Word2VecModels:
    def __init__(self) -> None:
        all_models: list = []
        model_data: dict = gensim_api.info()
        self.__models: dict = {}

        for model_name in model_data['models']:
            # We check this in try-except because some models are only for test purposes, so
            # they don't have the required attributes
            try:
                name: str = str(model_name)
                model: dict = model_data['models'][model_name]
                all_models.append((name, model['file_size'], model['parameters']['dimension']))
            except (KeyError,):
                pass

        if len(all_models) <= 0:
            raise Exception('No models found')
        all_models: list = sorted(all_models, key=lambda x: x[1])

        for idx, model in enumerate(all_models):
            self.__models[idx] = Model(model[0], model[1], model[2])

    def get_model_by_name(self, name: str) -> Model:
        """
        :param name: string - name of the target model
        :return: StringHelper.Model - returns model with the target name
        """
        return self.__models[name]

    def get_model_by_size(self, size: int) -> Model:
        """
        :param size: int - size of the target model
        :return: StringHelper.Model - returns target model
        """
        return self.__models[size]

    def get_smallest_model(self) -> Model:
        """
        :return: StringHelper.Model -  returns the smallest model
        """
        return self.__models[0]

    def get_largest_model(self) -> Model:
        """
        :return: StringHelper.Model - returns the largest model
        """
        return self.__models[len(self.__models) - 1]

    def get_model_by_idx(self, idx: int) -> Model:
        """
        :param idx: int - index of the target model
        :return: StringHelper.Model - returns target model
        """
        return self.__models.get(idx, None)


class StringHelper:
    def __init__(self, model: Model) -> None:
        self.__model: Model = model
        self.wv: dict = gensim_api.load(model.name)
        self.__stemmer: nltk.PorterStemmer = nltk.PorterStemmer()

    @staticmethod
    def tokenize(text: str) -> list:
        """
        :param text: string - text to be tokenized
        :return: returns text split into a list of tokens
        """
        return word_tokenize(text)

    def w2v(self, w: str) -> np.ndarray:
        """
        :param w: string - word to be converted to a vector
        :return: np.ndarray - returns a vector representation of the word
        """
        return self.wv[w]

    def stem(self, w: str) -> str:
        """
        :param w: string - word to be stemmed
        :return: string - returns the stemmed word
        """
        return self.__stemmer.stem(w)

    def get_dimensions(self) -> int:
        """
        :return: int - returns the dimensions of the Word2Vec model
        """
        return self.__model.dimensions

    def get_token_length(self, s: str) -> int:
        """
        :param s: string - string to be tokenized
        :return: int - returns the length of the tokenized string
        """
        return len(self.tokenize(s))

    def get_insertable(self, s: str, max_token_length: int, is_input: bool = False) -> np.ndarray:
        """
        :param s: string - string to be converted to a vector
        :param max_token_length: int - maximum length of the string
        :param is_input: bool - if the string is user input or not
        :return: np.ndarray - returns a vector representation of the string
        """
        current_sentence: list = []
        runs: int = 0
        for token in self.tokenize(s):
            if token in ['?', '!', '.', ',']:
                continue
            token: str = self.stem(token)
            try:
                current_sentence.append(self.w2v(token))
            except (KeyError,):
                current_sentence.append(np.zeros((self.__model.dimensions,)))
            runs += 1
        if runs > max_token_length:
            raise Exception(f'The sentence {s} is longer then the maximum token length ({max_token_length})')
        for _ in range(max_token_length - len(current_sentence)):
            current_sentence.append(np.zeros((self.__model.dimensions,)))
        current_sentence: np.ndarray = np.array(current_sentence)
        # To prevent incompatible shape errors we have to reshape the array
        if not is_input:
            return current_sentence.reshape(
                (current_sentence.shape[0], current_sentence.shape[1]))
        return current_sentence.reshape(
            (1, current_sentence.shape[0], current_sentence.shape[1]))

    def get_model_name(self) -> str:
        """
        :return: string - returns the name of the Word2Vec model
        """
        return self.__model.name
