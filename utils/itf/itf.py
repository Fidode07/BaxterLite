# ITF stands for "Important Token Finder" and tells you where important parts in a sentence are.

import json
import logging
from utils.config_helper import ConfigHelper
from utils.string_helper import StringHelper
from tensorflow import keras
from typing import *
import numpy as np
import os
from dataclasses import dataclass
import random

keras.mixed_precision.set_global_policy('mixed_float16')


@dataclass
class PositionPrediction:
    part1_start: float
    part1_end: float

    part2_start: float
    part2_end: float

    part3_start: float
    part3_end: float

    part4_start: float
    part4_end: float

    part5_start: float
    part5_end: float

    part6_start: float
    part6_end: float


class TokenDetector:
    def __init__(self, config_helper: ConfigHelper, str_helper: StringHelper, intent_paths: List[str],
                 use_pretrained: bool = False) -> None:
        """
        :param config_helper: ConfigHelper instance
        :param str_helper: StringHelper instance
        :param intent_paths: List[str] - path(s) to the intent dataset(s) of TokenDetector
        :param use_pretrained: Boolean - whether to use a pretrained model or not
        """
        self.__str_helper: StringHelper = str_helper
        self.__token_detector: Union[keras.Sequential, None] = None
        if use_pretrained and os.path.exists(
                f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5'):
            self.__token_detector = keras.models.load_model(
                f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5')
            logging.info(f'Loaded pretrained model token_detector-{self.__str_helper.get_model_name()}.h5')
        if use_pretrained and not os.path.exists(
                f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5'):
            logging.warning(f'No pretrained model token_detector-{self.__str_helper.get_model_name()}.h5 found. '
                            f'You have to train a new one via. token_detector.train()')

        self.__max_token_length: int = config_helper.get_config_setting('max_token_length')
        if not self.__max_token_length or not isinstance(self.__max_token_length, int):
            raise Exception('max_token_length is not set in config.json or is not an integer.')
        self.__intent_paths: List[str] = intent_paths
        self.__dataset_url: str = ('https://cdn.discordapp.com/attachments/1057089742262509659/1160679686058291320'
                                   '/output-dataset.json')

    def is_usable(self) -> bool:
        return self.__token_detector is not None

    def download_dataset(self) -> None:
        """
        Downloads the dataset from the dataset_url.
        :return: None
        """
        import requests
        import os
        if os.path.isfile('datasets/itf/output-dataset.json'):
            logging.info('Dataset already downloaded.')
            return
        logging.info('Downloading dataset ...')
        os.makedirs('datasets/itf', exist_ok=True)
        with open('datasets/itf/output-dataset.json', 'wb') as f:
            f.write(requests.get(self.__dataset_url).content)
        logging.info('Downloaded dataset.')

    def get_important_parts(self, s: str) -> PositionPrediction:
        """
        :param s: string - sentence to classify
        :return: Tuple[int, int] - start and end index of the token
        """
        if self.__token_detector is None:
            raise Exception('Token detector not trained yet. Please call train() first.')
        prediction: np.ndarray = self.__token_detector.predict(
            self.__str_helper.get_insertable(s.lower(), self.__max_token_length, True))
        return PositionPrediction(float(prediction[0][0]), float(prediction[0][1]),
                                  float(prediction[0][2]), float(prediction[0][3]),
                                  float(prediction[0][4]), float(prediction[0][5]),
                                  float(prediction[0][6]), float(prediction[0][7]),
                                  float(prediction[0][8]), float(prediction[0][9]),
                                  float(prediction[0][10]), float(prediction[0][11]))

    @staticmethod
    def __get_part_info(labels: tuple, index: int) -> list:
        """
        Returns the start and end index of a part, if found. Else returns -1 for both.
        :param labels: list - list of labels
        :param index: Index of label
        :return:
        """
        if len(labels) > index:
            return [labels[index][1], labels[index][2]]
        return [-1, -1]

    def train(self, epochs: int = 500, batch_size: int = 128, train_on_pretrained: bool = False) -> None:
        """
        Runs the training process of the token detector.
        :param epochs: int - number of epochs
        :param batch_size: int - how many samples to train on at once
        :param train_on_pretrained: Boolean - whether to train on the pretrained model or create a new one
        :return: None
        """

        features: list = []
        labels: list = []

        if not os.path.exists('datasets/itf/output-dataset.json'):
            self.download_dataset()
            if 'datasets/itf/output-dataset.json' not in self.__intent_paths:
                self.__intent_paths.append('datasets/itf/output-dataset.json')

        # Load all datasets and append them to the features and labels list
        for intent_path in self.__intent_paths:
            with open(intent_path, 'r', encoding='utf-8') as f:
                dataset: dict = json.load(f)
            for idx, entry in enumerate(dataset['intents']):
                sentence: str = str(entry['pattern']).lower()
                if self.__str_helper.get_token_length(sentence) > self.__max_token_length:
                    continue
                label: tuple = entry['labels']
                # labels.append(np.array([label[0][1], label[0][2],
                #                         label[1][1], label[1][2],
                #                         label[2][1], label[2][2]]))
                # dataset has labels list and in labels list there a lists in which the first item is the type
                # (we ignore this for now) and the second item is the start index and the third item is the end index
                # ive checked the dataset and there are max 6 lists in the labels list. If there are less than 6 lists
                # we put -1 values in here
                to_extend: list = []
                for i in range(6):
                    to_extend.extend(self.__get_part_info(label, i))
                labels.append(np.array(to_extend))
                features.append(
                    self.__str_helper.get_insertable(sentence, self.__max_token_length).astype(np.float32))
                # break after 100 entries to speed up training
                if idx > 50_000:
                    break
            del dataset

        features: np.ndarray = np.array(features)
        labels: np.ndarray = np.array(labels)

        # Shuffle the features and labels
        c: list = list(zip(features, labels))
        random.shuffle(c)
        features, labels = zip(*c)
        features: np.ndarray = np.array(features)
        labels: np.ndarray = np.array(labels)

        if train_on_pretrained:
            if os.path.isfile(f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5'):
                self.__token_detector = keras.models.load_model(
                    f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5')
                self.__token_detector.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])
                self.__token_detector.fit(features, labels, epochs=epochs, batch_size=batch_size,
                                          validation_split=.2)
                self.__token_detector.save(
                    f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5')
                return
            logging.warning('No pretrained model found. Training a new one ...')

        # Create the model
        self.__token_detector = keras.Sequential([
            keras.layers.LSTM(128 * 2, input_shape=(self.__max_token_length, self.__str_helper.get_dimensions()),
                              return_sequences=True, activation='relu'),
            keras.layers.Dropout(.2),
            keras.layers.LSTM(128 * 2, activation='relu'),
            keras.layers.Dropout(.2),
            keras.layers.Dense(64 * 2, activation='relu'),
            keras.layers.Dense(12)
        ])

        self.__token_detector.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='mean_squared_error',
                                      metrics=['accuracy'])
        self.__token_detector.fit(features, labels, epochs=epochs, batch_size=batch_size, validation_split=.2)
        self.__token_detector.save(f'models/pretrained/token_detector-{self.__str_helper.get_model_name()}.h5')

    # model_helper: Word2VecModels = Word2VecModels()
# target_model: Model = model_helper.get_smallest_model()
# str_helper: StringHelper = StringHelper(target_model)
#
# token_finder: TokenDetector = TokenDetector(str_helper, ['../datasets/itf/web-intents.json'], use_pretrained=True)
# # For 8GB VRAM and 16GB RAM and RTX 3050 we can use higher batch sizes
# token_finder.train(epochs=50, batch_size=256)
#
# test_sentence: str = 'open google.com in firefox'
# print(token_finder.get_token(test_sentence))