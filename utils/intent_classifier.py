from utils.string_helper import StringHelper
from utils.config_helper import ConfigHelper
from tensorflow import keras
import numpy as np
import json
from typing import *
from dataclasses import dataclass
import os


# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

@dataclass
class Prediction:
    tag: str
    confidence: float
    action: Optional[str] = None
    main_str: Optional[str] = None
    error_str: Optional[str] = None


@dataclass
class Intent:
    main_str: str
    error_str: str


class Classifier:
    def __init__(self, config_helper: ConfigHelper, str_helper: StringHelper, intent_path: str,
                 use_pretrained: bool = False) -> None:
        """
        :param str_helper: StringHelper instance
        :param intent_path: string - path to the intent dataset
        """
        with open(intent_path, 'r', encoding='utf-8') as f:
            self.__dataset: dict = json.load(f)
        self.__max_token_lengths: int = config_helper.get_config_setting('max_token_length')
        if not self.__max_token_lengths or not isinstance(self.__max_token_lengths, int):
            raise Exception('max_token_length is not set in config.json or is not an integer.')

        self.__str_helper: StringHelper = str_helper
        self.__intent_detector: Union[keras.Sequential, None] = None
        self.__model_file: str = f'models/pretrained/intent_detector_{str_helper.get_model_name()}.h5'

        if use_pretrained and os.path.exists(self.__model_file):
            self.__intent_detector = keras.models.load_model(self.__model_file)
        self.__tags: dict = {}
        for idx, intent in enumerate(self.__dataset['intents']):
            tag: str = intent['tag']
            self.__tags[idx] = tag

    def tag_exists(self, tag: str) -> bool:
        """
        Checks if a tag exists
        :param tag: string - tag to check
        :return: bool - True if tag exists, False if not
        """
        for intent in self.__dataset['intents']:
            if intent['tag'] == tag:
                return True
        return False

    def action_exists(self, action: str) -> bool:
        """
        Checks if an action exists
        :param action: string - action to check
        :return: bool - True if action exists, False if not
        """
        for intent in self.__dataset['intents']:
            if intent['action'] == action:
                return True
        return False

    def get_intent_by_action(self, action: str) -> Union[Intent, None]:
        for intent in self.__dataset['intents']:
            if intent['action'] == action:
                return Intent(intent['responses'][0], intent['error_msg'])
        return None

    def is_usable(self) -> bool:
        return self.__intent_detector is not None

    def classify(self, s: str) -> Prediction:
        """
        :param s: string - sentence to classify
        :return: Prediction - tag and confidence
        """
        if self.__intent_detector is None:
            raise Exception(
                f'Intent detector with model {self.__str_helper.get_model_name()} not trained yet. Please call '
                f'train() first or set use_pretrained to True.')
        prediction: np.ndarray = self.__intent_detector.predict(
            self.__str_helper.get_insertable(s.lower(), self.__max_token_lengths, True))
        tag: str = self.__tags[np.argmax(prediction)]
        confidence: float = np.max(prediction)
        action: Optional[str] = None if self.__dataset['intents'][np.argmax(prediction)]['action'] is None else \
            self.__dataset['intents'][np.argmax(prediction)]['action']

        # main_str is a random string from responses list, it's not a real key
        main_str: Optional[str] = None if self.__dataset['intents'][np.argmax(prediction)]['responses'] is None else \
            np.random.choice(self.__dataset['intents'][np.argmax(prediction)]['responses'])

        # error_str is a key value from responses but can be None in that case we use
        # default value 'Etwas ist schiefgelaufen, tut mir leid.'
        error_str: Optional[str] = None if self.__dataset['intents'][np.argmax(prediction)]['error_msg'] is None else \
            self.__dataset['intents'][np.argmax(prediction)]['error_msg']
        if error_str is None:
            error_str = 'Etwas ist schiefgelaufen, tut mir leid.'
        return Prediction(tag, confidence, action, main_str, error_str)

    def train(self, epochs: int = 500, batch_size: int = 64) -> None:
        """
        Trains the intent detector (Note that if a pretrained model is available the training continues on that model)
        :param epochs: int - number of epochs
        :param batch_size: int - how many samples to train on at once
        :return: None
        """
        features: list = []
        labels: list = []

        for idx, intent in enumerate(self.__dataset['intents']):
            tag: str = intent['tag']
            self.__tags[idx] = tag
            for pattern in intent['patterns']:
                features.append(np.array(self.__str_helper.get_insertable(pattern, self.__max_token_lengths)))
                labels.append(idx)

        features: np.ndarray = np.array(features)
        labels: np.ndarray = np.array(labels)

        if not self.__intent_detector:
            self.__intent_detector = keras.Sequential = keras.Sequential([
                keras.layers.LSTM(128 * 2, input_shape=(self.__max_token_lengths, self.__str_helper.get_dimensions()),
                                  return_sequences=True),
                keras.layers.Dropout(0.2),
                keras.layers.LSTM(128 * 2),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(len(self.__tags.keys()), activation='softmax')
            ])
            self.__intent_detector.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
                                           metrics=['accuracy'])
        self.__intent_detector.fit(features, labels, epochs=epochs, batch_size=batch_size)
        os.makedirs('models/pretrained', exist_ok=True)
        self.__intent_detector.save(self.__model_file)
