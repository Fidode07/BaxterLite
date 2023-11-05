# 🔊 BaxterLite 🔊

What is Baxter? Baxter is a voice assistant that is supposed to help me here and there (currently chat based). It will
probably be converted to an API later, or be accessible via a WebSocket. So it will be accessible via Arduinos, mobile
apps and more. Currently he <strong>only speaks german</strong>.

Please note that BaxterLite is a project designed for easy extension and has a lot of helper functions and classes. You
should definitely read the README before implementing your own features, as they will probably save you a lot of work in
the end.

# 📙 What it can 📙

Since Baxter is only a side project and I also only add features that I can use myself, it is relatively small.
Therefore also the Lite. His features:

- Tell me when room 2 is free in my gym
- Get current time
- Clear the chat
- Repeat the last action
- Tell you a joke
- Say hello
- Say bye

# 🤖 Usage 🤖

- First you need to download or clone the project, then navigate to the downloaded folder:
  ```bash
  cd <cloned-repo-dir>
  ```

  BaxterLite comes with a few dependencies that we need to install first. For this we simply run the following command:
  ```bash
  pip install -r requirements.txt
  ```

  Good, now we just start the main.py and that's it, BaxterLite is ready to support you!
  ```bash
  python main.py
  ```

# 💥 Add an Action 💥

All "commands" that Baxter can do are called action. All actions are located
in ``utils/action_helper/actions/<name-of-action>-action.py``. To add your own action, follow the instructions below:

- Think about an action name. It should be meaningful and understandable. Action names use the snake case as a naming
  convention, for e.g. ``weather_forecast``.
- Create a new Python file, under ``utils/action_helper/actions/``. The file should have the name of your action to keep
  an overview.
- Write your code in the Python file you created (all inside a class that should be called ``<Name-Of-Action>-Action``).
  The function returns the response to the user and is called whenever the action is to be executed. An example would
  be:

  ```py
  class SomeAction:
      def get_response(self, input_str, main_response: str, error_str: str, action_utils: ActionUtils, trigger_infos: TriggerInfos) -> str:
          return main_response
  ```
  <strong>Note that ALL actions must have the function ``get_response``!</strong>


- As you can see, the function must take 5 parameters:
    - <strong>input_str</strong>: String (the user input)
    - <strong>main_response</strong>: String (the response that the user gets when the action is executed from
      intents.json)
    - <strong>error_str</strong>: String (the response that the user gets when the action went wrong)
    - <strong>action_utils</strong>: ActionUtils Class (a class that contains some useful functions, e.g. to find
      important parts in the user input)
    - <strong>trigger_infos</strong>: TriggerInfos Class (a class that contains some useful information about the
      trigger, e.g. the confidence of the classifier)
- The code is ready and working? You have a get_response? Cool! Now we need to tell the action_helper that you created
  an action. For this we simply go to ``utils/action_helper/action_helper.py`` and first to the init method. There will
  be a dictionary that looks something like this:

  ```py
  self.__actions: dict = {
    'check_fightclub_room2': fightub_action.FightclubAction()
  }
  ```
  At the top you had to come up with a name for your action, we will enter it here. And as key an <strong>instance of
  your action class</strong>. The dictionary should look like this (if your action is called ``weather_forecast``):

  ```py
  self.__actions: dict = {
    'check_fightclub_room2': fightub_action.FightclubAction(),
    'weather_forecast': weather_forecast_action.WeatherForecastAction()
  }
  ```

  We go to the top of the ``action_helper.py`` and import the class created before. The import should look like this:

  ```py
    from utils.action_helper.actions import fightub_action, weather_forecast_action
  ```

- Great, that was almost everything we need to do in the code. Now there are only 2 steps missing. Let's start with the
  second last one, we need to edit the intents.json, which is under ``datasets/intents.json``. We need to navigate to
  the intents list and now add a new element. The element MUST have the following key value pairs!
    - <strong>tag</strong>: ``String`` -> something that explain short your action name (snake_case)
    - <strong>patterns</strong>: ``List of strings`` -> a list of possible sentences how a user can call your action
    - <strong>responses</strong>: ``List of strings`` -> possible responses of your action
    - <strong>action</strong>: ``String or null`` -> the action name you've created in step 1
    - <strong>error_msg</strong>: ``String`` -> An error message that the user gets when your action went wrong
      In this example, the new element would look like this:
  ```json
  {
    "tag": "get_weather_forecast",
    "patterns": [
      "how is the weather outside",
      "give me a weather forecast"
    ],
    "responses": [
      "outside are {forecast} degrees"
    ],
    "action": "weather_forecast",
    "error_msg": "Unable to get weather forecast, sorry"
  }
  ```
  Now save the ``intents.json`` file and do the last step.
- Whenever the ``intents.json`` is changed, you have to train the classifier again. For this we first go to ``main.py``.
  You will find a line that looks something like this:

  ```py
  classifier: Classifier = Classifier(str_helper, 'datasets/intents.json', use_pretrained=True)
  ```
  To train that thing, we just add a line, in the whole it should look like this:

  ```py
  classifier: Classifier = Classifier(str_helper, 'datasets/intents.json', use_pretrained=True)
  classifier.train(epochs=50)
  ```

Pouh, that was a long tutorial. Anyway, now you can just launch the application and call the action.

# 🛠️ TriggerInfos 🛠️

The TriggerInfos class is a class that contains some useful information about the trigger. You can find it under
``utils/action_utils/``. The class is a data class and contains the following attributes:

- <strong>ui</strong>: webview.Window (the window from which the trigger was made)
- <strong>last_action</strong>: str | None (the last action that was executed)
- <strong>last_input</strong>: str | None (the last input that was executed)

# 🛠️ ActionUtils 🛠️

The ActionUtils class is a class that contains some useful functions. You can find it under ``utils/action_utils.py``.
The class contains the following functions:

- get_important_parts(string) -> PositionPrediction

  Returns PositionPrediction Class (contains for each important part start-idx and end-idx, if nothing found it will be
  minus value)
  Example:

  ```py
  input_str: str = 'open google.com'
  
  token_detector: TokenDetector = action_utils.get_token_detector()
  position_prediction: PositionPrediction = token_detector.get_important_parts(input_str)

  website_start: int = round(position_prediction.part1_start)
  website_end: int = round(position_prediction.part1_end)
  
  website: str = action_utils.get_part_by_indexes(input_str, website_start, website_end)
  print(website) # -> is google.com
  ```
- get_config_helper() -> ConfigHelper

  Returns an instance of the ConfigHelper class
  Example:

  ```py
  class OpenWebsiteAction:
    @classmethod
    def get_response(cls, input_str: str, main_str: str, error_str: str, action_utils: ActionUtils, trigger_infos: TriggerInfos) -> str:
        config_helper: ConfigHelper = action_utils.get_config_helper()
  ```
- get_part_by_indexes(string, int, int) -> str

  Returns the location in a string that is between the given indexes.
  Example:

  ```py
  class OpenWebsiteAction:
    @classmethod
    def get_response(cls, input_str: str, main_str: str, error_str: str, action_utils: ActionUtils, trigger_infos: TriggerInfos) -> str:
        test_str: str = 'This is an example sentence' # goal is to get "example sentence"
        start_idx: 3
        end_idx: 4

        result: str = action_utils.get_part_by_indexes(test_str, start_idx, end_idx) # should be "example sentence"
  ```
- handle_if_statements(string) -> str

  Executes an if statement in the string, checking the config for values. Returns the executed string. The sample config
  looks like this:
  ```json
  {
    "name": "Fido"
  }
  ```

  Let's say the main_str looks like this:
  ```
  Hello%if_name%, {name}%if_name_end%!
  ```
  As you can see the if statement starts with <strong>%if_name%</strong>A. The _ says that now comes the key to search
  for in the config. It does <strong>not check the value</strong> of this key, but whether the key exists at all.

  Then comes <strong>{name}</strong>. Here the value of the key name is fetched from the Config and inserted. After that
  the if statement is <strong>closed with a %if_name_end%</strong>. Here the key <strong>MUST</strong> be the same as
  when opening.

  A simple action that handles these if statements looks like this:

  ```py
  import webview
  class GreetAction:
    @classmethod
    def get_response(cls, input_str: str, main_str: str, error_str: str, action_utils: ActionUtils, trigger_infos: TriggerInfos) -> str:
      test_str: str = 'Hello%if_name%, {name}%if_name_end%!'      
      result: str = action_utils.handle_if_statements(main_str) # since name exists in Config it will result in "Hello, Fido!" otherwhise it would end in "Hello!"
      return result
  ```
- get_token_detector() -> TokenDetector
      Returns an instance of the TokenDetector class
      Example:
    
    ```py
    class OpenWebsiteAction:
    @classmethod
    def get_response(cls, input_str: str, main_str: str, error_str: str, action_utils: ActionUtils, trigger_infos: TriggerInfos) -> str:
      token_detector: TokenDetector = action_utils.get_token_detector()
    ```

# ©️ Copyright ©️

BaxterLite was programmed by <a href="https://github.com/Fidode07">Fidode07</a>.
