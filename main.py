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
        return
    model_class.train(epochs=epochs)
    # TODO: Make instance check and load pretrained model if available


def main() -> None:
    model_helper: Word2VecModels = Word2VecModels()
    target_model: Model = model_helper.get_model_by_idx(5)
    config_helper: ConfigHelper = ConfigHelper(config_path='config.json')

    str_helper: StringHelper = StringHelper(target_model)
    token_detector: TokenDetector = TokenDetector(config_helper=config_helper, str_helper=str_helper,
                                                  intent_paths=['datasets/itf/output-dataset.json',
                                                                # 'datasets/itf/domain_dataset.json'],
                                                                ],
                                                  use_pretrained=True)
    # TODO: Add downloader for domain_dataset.json
    init_model(token_detector,
               25)  # NOTE: You should always prefer the pretrained model since it is trained on a huge dataset
    # and the training process takes a lot of time.
    # token_detector.train(epochs=10, train_on_pretrained=True)

    classifier: Classifier = Classifier(config_helper, str_helper, 'datasets/intents.json', use_pretrained=True)
    init_model(classifier, 200)
    classifier.train(epochs=200)

    action_helper: ActionHelper = ActionHelper(config_helper=config_helper,
                                               token_detector=token_detector,
                                               classifier=classifier)

    ui_title: str = config_helper.get_config_setting('ui_title')
    ui_width: int = config_helper.get_config_setting('ui_width')
    ui_height: int = config_helper.get_config_setting('ui_height')

    ui: Ui = Ui(title=ui_title, width=ui_width, height=ui_height, classifier=classifier, action_helper=action_helper,
                config_helper=config_helper)
    Thread(target=TrayHelper.run_from_thread, args=(ui,)).start()
    Thread(target=thread_helper, args=(ui,)).start()
    webview.start()


if __name__ == '__main__':
    main()
