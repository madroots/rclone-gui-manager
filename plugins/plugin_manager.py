"""
Plugin manager for Rclone GUI Manager
Handles loading, registering, and managing remote plugins
"""

import os
import importlib.util
from pathlib import Path
from typing import List, Dict, Type
from .plugin_interface import RemotePlugin


class PluginManager:
    """Manages the loading and registration of remote plugins"""
    
    def __init__(self, plugins_dir: str = None):
        self.plugins_dir = plugins_dir or os.path.dirname(__file__)
        self._plugins: Dict[str, Type[RemotePlugin]] = {}
        self._instances: Dict[str, RemotePlugin] = {}

        # Create plugins directory if it doesn't exist
        Path(self.plugins_dir).mkdir(exist_ok=True)
        
    def load_plugins(self):
        """Load all available plugins from the plugins directory"""
        self._plugins = {}
        self._instances = {}
        
        # Look for Python files in the plugins directory
        for file_path in Path(self.plugins_dir).glob("*.py"):
            if file_path.name == "__init__.py" or file_path.name == "plugin_interface.py":
                continue
                
            plugin_name = file_path.stem
            try:
                # Load the plugin module
                spec = importlib.util.spec_from_file_location(plugin_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for a class that inherits from RemotePlugin
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, RemotePlugin) and 
                        attr != RemotePlugin):
                        
                        # Register the plugin class
                        self._plugins[plugin_name] = attr
                        # Create an instance for reference
                        self._instances[plugin_name] = attr()
                        break
                        
            except Exception as e:
                print(f"Error loading plugin {plugin_name}: {e}")
                
    def get_available_plugins(self) -> List[str]:
        """Return a list of available plugin names"""
        return list(self._plugins.keys())
    
    def get_plugin(self, name: str) -> RemotePlugin:
        """Get an instance of a plugin by name"""
        return self._instances.get(name)
    
    def get_plugin_class(self, name: str) -> Type[RemotePlugin]:
        """Get the plugin class by name"""
        return self._plugins.get(name)
    
    def get_plugin_info(self, name: str) -> Dict[str, any]:
        """Get information about a plugin"""
        plugin = self.get_plugin(name)
        if not plugin:
            return {}
            
        return {
            'name': plugin.get_name(),
            'description': plugin.get_description(),
            'notes': plugin.get_notes(),
            'requires_oauth': plugin.requires_oauth(),
        }