import logging
import os
import importlib
from typing import *

from utils.intent_classifier import Classifier


class PluginManager:
    def __init__(self, classifier: Classifier) -> None:
        self.__plugins: dict = {}
        self.__plugin_actions: dict = {}

        # Init plugins
        os.makedirs('plugins', exist_ok=True)
        for plugin in os.listdir('plugins'):
            if not plugin.endswith('.py'):
                continue
            module_name: str = f'plugins.{plugin[:-3]}'
            plugin_data: Callable = self.get_plugin_data(module_name)
            plugin_instance: Any = plugin_data()

            try:
                plugin_name: str = plugin_instance.get_name()
            except AttributeError:
                logging.warning(f'Plugin {plugin} has no name. Skipping...')
                continue

            plugin_tag: str = 'plugin-' + plugin_name
            plugin_action: str = plugin_tag + '-action'

            if not all([classifier.tag_exists(plugin_tag), classifier.action_exists(plugin_action)]):
                logging.warning(f'Plugin {plugin_name} is not registered in the intent dataset. Skipping...')
                continue
            self.__plugins[plugin_tag] = plugin_instance
            self.__plugin_actions[plugin_action] = plugin_instance

            logging.info(f'Plugin {plugin_name} loaded successfully')

    def get_plugin_actions(self) -> dict:
        """
        This parses all plugins and returns a dictionary with all actions
        :return: dict - all actions
        """
        return self.__plugin_actions

    @staticmethod
    def get_plugin_data(module_name: str) -> Callable:
        """
        This function tries to get the plugin class (all plugin classes must be titled as "Plugin")
        :param module_name: string - name of the module to import
        :return: Callable - plugin class
        """
        plugin_module = importlib.import_module(module_name)
        plugin_class = getattr(plugin_module, 'Plugin')
        return plugin_class
