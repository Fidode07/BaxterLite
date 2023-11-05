import datetime
import json
import os.path
from utils.config_helper import ConfigHelper
from utils.action_utils import ActionUtils
import random
from dataclasses import dataclass
from typing import *
import locale
import bs4
from bs4 import BeautifulSoup as Soup
from bs4 import *
import numpy as np
import pytesseract
import requests as rq
from utils.exceptions import *
import cv2


@dataclass
class TimePair:
    start: str
    end: str


class TimePairEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TimePair):
            return {'start': obj.start, 'end': obj.end}
        return super().default(obj)


class FightclubAction:
    def __init__(self) -> None:
        self.__url: str = 'https://www.munichfightclub.de'
        self.__endpoints: List[str] = ['stundenplan', 'kids']
        self.__days: List[str] = ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag',
                                  'samstag', 'sonntag']
        os.makedirs(os.path.join(os.path.dirname(__file__), 'cache'), exist_ok=True)
        self.__cache_file: str = os.path.join(os.path.dirname(__file__), 'cache',
                                              self.__class__.__name__.lower() + '.json')

    def get_response(self, _: str, main_response: str, error_str: str, action_utils: ActionUtils,
                     __: object) -> str:
        config_helper: ConfigHelper = action_utils.get_config_helper()

        pytesseract.pytesseract.tesseract_cmd = config_helper.get_config_setting('tesseract_path')
        try:
            times: Dict[str, List[TimePair]] = self.__get_room_2_times()
            day: str = self.__get_weekday_name()
            today_times: List[TimePair] = times[day]  # -> course times (not available times)

            available_times: List[TimePair] = self.__get_available_times(today_times)

            response: str = self.__get_response_sentence(available_times)
            main_response = main_response.format(status_msg=response)
            return main_response
        except (Exception,):
            return error_str

    def __get_response_sentence(self, free_times: List[TimePair]) -> str:
        # We get something like 'Laut Internet ist {status_msg}', our job is to replace {status_msg} with the
        # correct sentence
        sentences: Dict[str, List[str]] = {'unavailable': ['der Raum heute leider nicht mehr verfügbar',
                                                           'der Raum heute leider nicht mehr frei']}
        if len(free_times) == 0:
            return random.choice(sentences['unavailable'])

        response: str = ''

        # check if current time is between ANY free_time pair if yes, return 'der Raum ist jetzt frei'
        today: datetime.datetime = datetime.datetime.now()
        current_time: datetime.time = today.time()

        for idx, pair in enumerate(free_times):
            start: datetime.time = datetime.datetime.strptime(pair.start, '%H:%M').time()
            end: datetime.time = datetime.datetime.strptime(pair.end, '%H:%M').time()
            if start <= current_time <= end:
                # calculate how long the room is free
                time_left: datetime.timedelta = datetime.datetime.combine(today.date(),
                                                                          end) - datetime.datetime.combine(today.date(),
                                                                                                           current_time)
                if time_left.seconds > 0:
                    response += 'der Raum zurzeit frei'
                    response += f', und bleibt es noch für die nächsten {time_left.seconds // 60} Minuten.'
                    # Calculate next possible time and add something 'die nächste mögliche Zeit wäre um 16:00 Uhr für
                    # 60 Minuten'. Trough the idx we can get the next possible time
                    if not len(free_times) > idx + 1:
                        # There is no next possible time
                        return response
                    next_free_time: TimePair = free_times[idx + 1]
                    possible_time: datetime.time = datetime.datetime.strptime(next_free_time.start, '%H:%M').time()
                    minutes: int = (datetime.datetime.combine(today.date(), possible_time) -
                                    datetime.datetime.combine(today.date(), end)).seconds // 60
                    response += f' Die nächste mögliche Zeit wäre um {possible_time.strftime("%H:%M")} Uhr für ' \
                                f'{minutes} Minuten.'
                else:
                    break
                return response
        # If we are here, the room is not free at the moment
        response += 'der Raum gerade leider nicht frei'
        # Calculate next possible time and add something 'die nächste mögliche Zeit wäre um 16:00 Uhr für
        # 60 Minuten'. iterate through the free_times list and get the next possible time
        for idx, pair in enumerate(free_times):
            start: datetime.time = datetime.datetime.strptime(pair.start, '%H:%M').time()
            end: datetime.time = datetime.datetime.strptime(pair.end, '%H:%M').time()
            if start > current_time:
                # We found the next possible time, calc start - end
                minutes: int = (datetime.datetime.combine(today.date(), end) -
                                datetime.datetime.combine(today.date(), start)).seconds // 60
                response += f', die nächste mögliche Zeit wäre um {start.strftime("%H:%M")} Uhr für {minutes} Minuten.'
                if minutes <= 30:
                    # add something like 'ansonsten wäre die nächste freie Zeit um 16:00 Uhr für 60 Minuten'
                    if not len(free_times) > idx + 1:
                        # There is no next possible time
                        return response
                    next_free_time: TimePair = free_times[idx + 1]
                    possible_time: datetime.time = datetime.datetime.strptime(next_free_time.start, '%H:%M').time()
                    possible_time_end: datetime.time = datetime.datetime.strptime(next_free_time.end, '%H:%M').time()
                    minutes: int = (datetime.datetime.combine(today.date(), possible_time_end) -
                                    datetime.datetime.combine(today.date(), possible_time)).seconds // 60
                    response += f' Ansonsten wäre die nächste freie Zeit um {possible_time.strftime("%H:%M")} Uhr ' \
                                f'für {minutes} Minuten.'
                return response

        response += ', leider gibt es heute auch keine weiteren freien Zeiten mehr.'
        return response

    def __get_available_times(self, course_times: List[TimePair]) -> List[TimePair]:
        today = datetime.datetime.now()
        close_time = datetime.time(22, 0) if today.weekday() < 5 else datetime.time(16, 0)

        open_time = datetime.time(8, 0)

        if open_time < today.time() < close_time:
            open_time = today.time()

        available_times = []

        while open_time < close_time:
            if len(course_times) == 0:
                to_add = TimePair(open_time.strftime('%H:%M'), close_time.strftime('%H:%M'))
                available_times.append(to_add)
                break
            next_course = min(course_times, key=lambda x: datetime.datetime.strptime(x.start, '%H:%M'))
            if datetime.datetime.strptime(next_course.start, '%H:%M').time() > open_time:
                # We have a free time
                available_times.append(TimePair(open_time.strftime('%H:%M'), next_course.start))
            open_time = datetime.datetime.strptime(next_course.end, '%H:%M').time()
            course_times.remove(next_course)
        return available_times

    def __get_weekday_name(self) -> str:
        locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

        today: datetime.date = datetime.date.today()
        weekday_name_german: str = today.strftime('%A')

        locale.setlocale(locale.LC_TIME, '')
        return weekday_name_german.lower()

    def __fetch_image_from_url(self, img_url: str) -> np.ndarray:
        img_request: rq.Response = rq.get(img_url)

        if img_request.status_code != 200:
            raise UnableToFetchImage(f'Sorry, can\'t fetch Image from {img_url}')

        img_array = np.frombuffer(img_request.content, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def __image_to_text(self, image_url: str) -> str:
        img: np.ndarray = self.__fetch_image_from_url(image_url)
        return pytesseract.image_to_string(img, lang='eng')

    def __get_room_2_times(self, use_cache: bool = True) -> Dict[str, List[TimePair]]:
        response: Dict[str, List[TimePair]] = {}
        if use_cache and os.path.isfile(self.__cache_file):
            return self.__get_times_from_cache()

        for endpoint in self.__endpoints:
            current_request: rq.Response = rq.get(f'{self.__url}/{endpoint}')
            soup: Soup = Soup(current_request.content, 'html.parser')

            if endpoint == 'stundenplan':
                # Fetch images
                section: Tag = soup.find('section', {'id': 'comp-lbm366042'})
                images: ResultSet = section.find_all('img')
                for img in images:
                    real_url: str = img['src'].split('/v1/')[0]
                    text: str = self.__image_to_text(real_url)
                    data: Dict[str, List[TimePair]] = self.__parse_text_to_dict(text)
                    response.update(data)
            if endpoint == 'kids':
                card_section: Tag = soup.find('section', {'id': 'comp-lbm33l4u1'})
                cards: ResultSet = card_section.find_all('div', {'class': 'Zc7IjY'})
                for card in cards:
                    data: Dict[str, List[TimePair]] = self.__parse_cards(card)
                    for day, item in data.items():
                        if day not in response:
                            response[day] = item
                            continue
                        # Already in
                        response[day].extend(item)
        with open(self.__cache_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(response, cls=TimePairEncoder))
        return response

    def __parse_text_to_dict(self, text: str) -> Dict[str, List[TimePair]]:
        lines: list = text.split('\n')
        return self.__parse_lines(lines)

    def __parse_lines(self, lines: List[str], main_day: str = None) -> Dict[str, List[TimePair]]:
        response: Dict[str, List[TimePair]] = {}

        current_day: str = main_day
        is_room_2_data: bool = False

        i: int = 0

        for line in lines:
            line = line.lower()
            for day in self.__days:
                if day.lower() in line:
                    current_day = day
                    is_room_2_data = False
                    break
            if 'raum 2' in line or 'room 2' in line:
                is_room_2_data = True
                i += 1
            if i == 0:
                continue
            if line is None:
                continue
            if len(line) == 0:
                continue

            if not is_room_2_data:
                continue

            if not line[0].isnumeric():
                continue
            time_text: list = line.split()[0].replace('.', ':').split('-')
            pair: TimePair = TimePair(time_text[0], time_text[1])
            if current_day not in response:
                response[current_day] = []
            response[current_day].append(pair)
        return response

    def __parse_cards(self, card: bs4.Tag) -> Dict[str, List[TimePair]]:
        main_day: str = card.find_all('h2')[0].text.lower()
        lines_to_send: List[str] = []
        lines: ResultSet = card.find_all('p')
        for line in lines:
            if line is None:
                continue
            lines_to_send.append(line.text.lower())
        return self.__parse_lines(lines_to_send, main_day)

    def __get_times_from_cache(self) -> Dict[str, List[TimePair]]:
        response: Dict[str, List[TimePair]] = {}
        try:
            cached_data: dict = json.load(open(self.__cache_file, 'r', encoding='utf-8'))
            for day in cached_data:
                response[day] = []
                for pair in cached_data[day]:
                    start: str = pair['start']
                    end: str = pair['end']
                    response[day].append(TimePair(start=start, end=end))
        except (Exception,):
            response = self.__get_room_2_times(use_cache=False)  # re-fetch data
        return response
