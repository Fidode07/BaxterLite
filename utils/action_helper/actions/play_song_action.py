import logging
from utils.action_utils import ActionUtils
from utils.itf.itf import TokenDetector, PositionPrediction
from typing import *


class PlaySongAction:
    def get_response(self, input_str: str, main_str: str, error_str: str, action_utils: ActionUtils) -> str:
        try:
            token_detector: TokenDetector = action_utils.get_token_detector()
            position_prediction: PositionPrediction = token_detector.get_important_parts(input_str)

            song_indexes: List[int] = [round(x) for x in
                                       [position_prediction.part1_start, position_prediction.part1_end]]
            artist_indexes: List[int] = [round(x) for x in
                                         [position_prediction.part2_start, position_prediction.part2_end]]
            platform_indexes: List[int] = [round(x) for x in
                                           [position_prediction.part3_start, position_prediction.part3_end]]

            song_indexes.sort()
            artist_indexes.sort()
            platform_indexes.sort()

            song_name: str = action_utils.get_part_by_indexes(input_str, song_indexes[0], song_indexes[1])
            artist_name: str = action_utils.get_part_by_indexes(input_str, artist_indexes[0], artist_indexes[1])
            platform_name: str = action_utils.get_part_by_indexes(input_str, platform_indexes[0], platform_indexes[1])

            response: str = self.__get_response(main_str, song_name, artist_name, platform_name)
            if not response:
                return error_str
            return response
        except (Exception,) as e:
            logging.error(['[PlaySongAction -> get_response]', e])
            return error_str

    @staticmethod
    def __get_response(main_str: str, song_name: str, artist_name: str, platform_name: str) -> Union[str, None]:
        if not song_name:
            return 'Tut mir leid, ich konnte keinen Songnamen erkennen'
        # possible: artist_name AND platform_name
        if artist_name and platform_name:
            return main_str.format(song_name=song_name, artist_name=artist_name, platform_name=platform_name)
        # possible: artist_name OR platform_name
        if artist_name:
            return main_str.format(song_name=song_name, artist_name=artist_name, platform_name='YouTube')
        if platform_name:
            return main_str.format(song_name=song_name, artist_name='Unknown', platform_name=platform_name)
        # possible: nothing
        return None
