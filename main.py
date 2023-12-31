import time
from utils.action_helper.action_helper import ActionHelper
from utils.config_helper import ConfigHelper
from utils.string_helper import StringHelper, Model, Word2VecModels
from utils.itf.itf import TokenDetector
from utils.intent_classifier import Classifier
from utils.ui.ui_helper import Ui, webview
from utils.tray_helper.tray_helper import TrayHelper
from utils.hook_helper import thread_helper
from threading import Thread
from tensorflow import keras
from typing import *

keras.mixed_precision.set_global_policy('mixed_float16')


def init_model(model_class: Union[Classifier, TokenDetector], epochs: int) -> None:
    if model_class.is_usable():
        if isinstance(model_class, Classifier):
            model_class.train(epochs=20)  # make sure that the model is trained on the new dataset
        return
    model_class.train(epochs=epochs)
    # TODO: Make instance check and load pretrained model if available


def show_startup_message() -> None:
    msg_width: int = 75
    program_name: str = 'BaxterLite'
    author: str = 'by Fido_de07'
    print('-' * msg_width)
    print(f'{program_name:^{msg_width}}')
    print(f'{author:^{msg_width}}')
    # print('\nNOTE: This program can take a while to start up, so please be patient.')
    print(f'{"NOTE: This program can take a while to start up, so please be patient.":^{msg_width}}')
    print('-' * msg_width)


def main() -> None:
    show_startup_message()
    start: float = time.time()

    model_helper: Word2VecModels = Word2VecModels()
    target_model: Model = model_helper.get_model_by_idx(5)
    # target_model: Model = model_helper.get_model_by_idx(0)
    config_helper: ConfigHelper = ConfigHelper(config_path='config.json')

    str_helper: StringHelper = StringHelper(target_model)
    token_detector: TokenDetector = TokenDetector(config_helper=config_helper, str_helper=str_helper,
                                                  intent_paths=[],
                                                  use_pretrained=True)
    init_model(token_detector,
               115)  # NOTE: You should always prefer the pretrained model since it is trained on a huge dataset
    # and the training process takes a lot of time.
    # token_detector.train(epochs=10, train_on_pretrained=True)

    classifier: Classifier = Classifier(config_helper, str_helper, 'datasets/intents.json', use_pretrained=True)
    init_model(classifier, 200)

    action_helper: ActionHelper = ActionHelper(config_helper=config_helper,
                                               token_detector=token_detector,
                                               classifier=classifier)

    ui_title: str = config_helper.get_config_setting('ui_title')
    ui_width: int = config_helper.get_config_setting('ui_width')
    ui_height: int = config_helper.get_config_setting('ui_height')

    ui: Ui = Ui(title=ui_title, width=ui_width, height=ui_height, classifier=classifier, action_helper=action_helper,
                config_helper=config_helper)

    action_helper.set_ui(ui)

    Thread(target=TrayHelper.run_from_thread, args=(ui, config_helper)).start()
    Thread(target=thread_helper, args=(ui,)).start()

    print(f'Startup in {time.time() - start} seconds')

    webview.start(debug=False)


if __name__ == '__main__':
    main()
