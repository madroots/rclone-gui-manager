# Contributing to Rclone GUI Manager

Thank you for your interest in contributing to the Rclone GUI Manager! This guide will help you understand how to add new remote types through plugins.

## Table of Contents
- [Adding New Remote Types](#adding-new-remote-types)
- [Plugin Development](#plugin-development)
- [Plugin Interface](#plugin-interface)
- [Plugin Template](#plugin-template)
- [Field Types](#field-types)
- [Testing Your Plugin](#testing-your-plugin)
- [Submitting Your Plugin](#submitting-your-plugin)

## Adding New Remote Types

The Rclone GUI Manager uses a plugin architecture to support different remote types. To add a new remote type, you need to create a plugin that implements the required interface.

## Plugin Development

### File Structure
Create your plugin in the `plugins/` directory with the naming convention `remote_name_plugin.py`. For example, `s3_plugin.py`.

### Required Imports
```python
from plugins.plugin_interface import RemotePlugin, PluginField, PluginResult
import subprocess
import tempfile
import os
```

## Plugin Interface

Your plugin class must inherit from `RemotePlugin` and implement the following methods:

### Required Methods

#### `get_name() -> str`
Return the display name of the remote type.

```python
def get_name(self) -> str:
    return "SFTP"
```

#### `get_fields() -> List[PluginField]`
Define the configuration fields required for this remote type.

```python
def get_fields(self) -> list:
    return [
        PluginField(
            name="host",
            label="Host",
            field_type="text",
            required=True,
            description="The host to connect to"
        ),
        # ... more fields
    ]
```

#### `validate_config(config: dict) -> PluginResult`
Validate the provided configuration values.

```python
def validate_config(self, config: dict) -> PluginResult:
    errors = []
    if not config.get('host'):
        errors.append("Host is required")
    
    if errors:
        return PluginResult(False, "; ".join(errors))
    
    return PluginResult(True, "Configuration appears valid")
```

#### `test_connection(config: dict) -> PluginResult`
Test connection with the provided configuration.

```python
def test_connection(self, config: dict) -> PluginResult:
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
        f.write(f"[test-remote]\n")
        f.write(f"type = sftp\n")
        for key, value in config.items():
            if value:
                f.write(f"{key} = {value}\n")
        temp_config_path = f.name

    try:
        result = subprocess.run([
            'rclone', 'lsf', 'test-remote:/',
            f'--config={temp_config_path}'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return PluginResult(True, "Connection successful")
        else:
            return PluginResult(False, f"Connection failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        return PluginResult(False, "Connection test timed out")
    except Exception as e:
        return PluginResult(False, f"Connection test failed: {str(e)}")
    finally:
        os.unlink(temp_config_path)
```

#### `get_config_format(config: dict) -> dict`
Return the rclone.conf format for this remote type.

```python
def get_config_format(self, config: dict) -> dict:
    result = {'type': 'sftp'}
    for key, value in config.items():
        if value:
            result[key] = value
    return result
```

### Optional Methods

#### `get_description() -> str`
Return a description of this remote type.

```python
def get_description(self) -> str:
    return "SSH File Transfer Protocol - Secure file transfer over SSH"
```

#### `get_notes() -> str`
Return special notes or warnings for this remote type.

```python
def get_notes(self) -> str:
    return """Important notes:
- Password authentication is less secure than key-based authentication
- For key-based auth, ensure your SSH key has proper permissions (typically 600)"""
```

#### `get_advanced_fields() -> List[PluginField]`
Return additional advanced fields (optional).

```python
def get_advanced_fields(self) -> List[PluginField]:
    return [
        PluginField(
            name="ask_password",
            label="Ask for Password",
            field_type="bool",
            required=False,
            description="Always ask for password interactively"
        )
    ]
```

## Plugin Template

Here's a template you can use to create new plugins:

```python
"""
[Remote Name] plugin for Rclone GUI Manager
"""

from plugins.plugin_interface import RemotePlugin, PluginField, PluginResult
import subprocess
import tempfile
import os


class [RemoteName]Plugin(RemotePlugin):
    
    def get_name(self) -> str:
        return "[Remote Name]"
    
    def get_description(self) -> str:
        return "[Brief description of the remote type]"
    
    def get_notes(self) -> str:
        return """[Important notes or warnings for users]"""

    def get_fields(self) -> list:
        return [
            PluginField(
                name="host",
                label="Host",
                field_type="text",
                required=True,
                description="The host to connect to"
            ),
            PluginField(
                name="username",
                label="Username",
                field_type="text",
                required=True,
                description="Your username"
            ),
            PluginField(
                name="password",
                label="Password",
                field_type="password",
                required=True,
                description="Your password"
            ),
            # Add more fields as needed
        ]

    def get_advanced_fields(self) -> list:
        return [
            PluginField(
                name="port",
                label="Port",
                field_type="int",
                required=False,
                default="22",
                description="Port number (default: 22)"
            ),
            # Add advanced fields as needed
        ]

    def validate_config(self, config: dict) -> PluginResult:
        # Basic validation
        errors = []
        
        if not config.get('host'):
            errors.append("Host is required")
        
        if not config.get('username'):
            errors.append("Username is required")
        
        if errors:
            return PluginResult(False, "; ".join(errors))
        
        return PluginResult(True, "Configuration appears valid")

    def test_connection(self, config: dict) -> PluginResult:
        # Create a temporary rclone config file with just this remote
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
            f.write(f"[test-remote]\n")
            f.write(f"type = [remote-type]\n")
            for key, value in config.items():
                if value:  # Only write non-empty values
                    f.write(f"{key} = {value}\n")
            temp_config_path = f.name

        try:
            # Test the connection by listing the root directory
            result = subprocess.run([
                'rclone', 'lsf', 'test-remote:/', 
                f'--config={temp_config_path}'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return PluginResult(True, "Connection successful")
            else:
                return PluginResult(False, f"Connection failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            return PluginResult(False, "Connection test timed out")
        except Exception as e:
            return PluginResult(False, f"Connection test failed: {str(e)}")
        finally:
            # Clean up the temporary config file
            os.unlink(temp_config_path)

    def get_config_format(self, config: dict) -> dict:
        # Return the format for rclone.conf
        result = {'type': '[remote-type]'}  # Replace [remote-type] with actual rclone type
        for key, value in config.items():
            if value:  # Only include non-empty values
                result[key] = value
        return result
```

## Field Types

The plugin system supports several field types:

- `"text"`: Regular text input
- `"password"`: Password field with hidden characters
- `"file"`: File selection with browse button
- `"choice"`: Dropdown selection with predefined options
- `"bool"`: Checkbox (True/False)
- `"int"`: Integer input
- `"float"`: Floating point number input

### File Field Example
```python
PluginField(
    name="key_file",
    label="Private Key File",
    field_type="file",
    required=False,
    file_filter="*.pem *.key *.ssh",
    description="Path to your SSH private key file"
)
```

### Choice Field Example
```python
PluginField(
    name="storage_type",
    label="Storage Type",
    field_type="choice",
    required=True,
    choices=["standard", "reduced_redundancy", "glacier"],
    default="standard",
    description="Choose storage class"
)
```

## Testing Your Plugin

1. Place your plugin file in the `plugins/` directory
2. Restart the Rclone GUI Manager application
3. The plugin should appear in the "Add New Remote" dialog
4. Test the configuration form and connection testing functionality
5. Verify that the remote is properly saved to the rclone config

## Submitting Your Plugin

1. Fork the repository
2. Create your plugin file in the `plugins/` directory
3. Add your plugin to a pull request with:
   - A clear description of the remote type
   - Any special requirements or notes for users
   - Test results confirming the plugin works

## Best Practices

- Always use secure methods for handling passwords and keys
- Provide clear, helpful descriptions for all fields
- Validate user inputs thoroughly
- Handle errors gracefully
- Test your plugin thoroughly before submitting

---

**Note**: For complex remote types requiring OAuth or special authentication flows, please contact the maintainers for guidance.