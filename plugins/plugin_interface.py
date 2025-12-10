"""
Plugin interface for Rclone GUI Manager
Defines the interface that all remote plugins must implement
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import os


class PluginField:
    """Represents a single field in a plugin configuration form"""
    def __init__(self, name: str, label: str, field_type: str = "text", 
                 required: bool = True, default: str = "", 
                 password: bool = False, file_filter: str = "", 
                 description: str = "", choices: List[str] = None):
        """
        name: Internal field name
        label: User-facing label
        field_type: "text", "password", "file", "choice", "bool", "int", "float"
        required: Whether the field is required
        default: Default value
        password: Whether this is a password field
        file_filter: File type filter for file fields (e.g., "*.pem")
        description: Optional description/help text
        choices: List of choices for choice fields
        """
        self.name = name
        self.label = label
        self.field_type = field_type
        self.required = required
        self.default = default
        self.password = password
        self.file_filter = file_filter
        self.description = description
        self.choices = choices or []


class PluginResult:
    """Represents the result of a plugin operation"""
    def __init__(self, success: bool, message: str, data: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.data = data or {}


class RemotePlugin(ABC):
    """Base interface for all remote plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the display name of the remote type (e.g., 'SFTP', 'Google Drive')"""
        pass

    @abstractmethod
    def get_fields(self) -> List[PluginField]:
        """Return a list of fields required for this remote type"""
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, str]) -> PluginResult:
        """Validate the provided configuration values"""
        pass

    @abstractmethod
    def test_connection(self, config: Dict[str, str]) -> PluginResult:
        """Test connection with provided configuration"""
        pass

    @abstractmethod
    def get_config_format(self, config: Dict[str, str]) -> Dict[str, Any]:
        """Return the rclone.conf format for this remote type"""
        pass

    def get_description(self) -> str:
        """Return a description of this remote type (optional)"""
        return ""

    def get_notes(self) -> str:
        """Return any special notes or warnings for this remote type (optional)"""
        return ""

    def requires_oauth(self) -> bool:
        """Return True if this remote requires OAuth (optional)"""
        return False

    def get_oauth_url(self, config: Dict[str, str]) -> Optional[str]:
        """Return the OAuth URL if this remote requires OAuth (optional)"""
        return None

    def handle_oauth_callback(self, code: str) -> PluginResult:
        """Handle OAuth callback with authorization code (optional)"""
        return PluginResult(False, "OAuth not implemented for this plugin")
    
    def get_advanced_fields(self) -> List[PluginField]:
        """Return additional advanced fields (optional)"""
        return []
    
    def get_wizard_pages(self) -> List[Dict[str, Any]]:
        """Return wizard pages for multi-step configuration (optional)"""
        return []