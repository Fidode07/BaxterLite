import webbrowser as wb

from utils.action_utils import ActionUtils
from utils.itf.itf import PositionPrediction


class OpenWebsiteAction:
    @classmethod
    def get_response(cls, input_str: str, main_str: str, error_str: str, action_utils: ActionUtils,
                     _: object) -> str:
        try:
            positions: PositionPrediction = action_utils.get_token_detector().get_important_parts(input_str)
            web_start_idx, web_end_idx = positions.part1_start, positions.part1_end
            if not all([web_start_idx, web_end_idx]):
                return error_str
            web_str: str = ActionUtils.get_part_by_indexes(input_str, round(web_start_idx), round(web_end_idx))
            wb.open_new_tab(web_str)
            return main_str.format(website=web_str)
        except (Exception,):
            return error_str
