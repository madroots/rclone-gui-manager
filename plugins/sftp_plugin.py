"""
SFTP plugin for Rclone GUI Manager
"""

from plugins.plugin_interface import RemotePlugin, PluginField, PluginResult
import subprocess
import tempfile
import os


class SFTPPlugin(RemotePlugin):
    
    def get_name(self) -> str:
        return "SFTP"
    
    def get_description(self) -> str:
        return "SSH File Transfer Protocol - Secure file transfer over SSH"
    
    def get_notes(self) -> str:
        return """Important notes:
- Password authentication is less secure than key-based authentication
- For key-based auth, ensure your SSH key has proper permissions (typically 600)
- If using a custom SSH port, make sure it's accessible
- Some servers may require specific SSH ciphers or options"""

    def get_fields(self) -> list:
        return [
            PluginField(
                name="host",
                label="Host",
                field_type="text",
                required=True,
                description="The host to connect to (e.g., example.com)"
            ),
            PluginField(
                name="user",
                label="Username",
                field_type="text",
                required=True,
                description="SSH username to use"
            ),
            PluginField(
                name="port",
                label="Port",
                field_type="int",
                required=False,
                default="22",
                description="SSH port number (default: 22)"
            ),
            PluginField(
                name="pass",
                label="Password",
                field_type="password",
                required=False,
                description="SSH password (leave empty if using key authentication)"
            ),
            PluginField(
                name="key_file",
                label="Private Key File",
                field_type="file",
                required=False,
                file_filter="*.pem *.key *.ssh",
                description="Path to SSH private key file (for key-based authentication)"
            ),
            PluginField(
                name="disable_hashcheck",
                label="Disable Hash Check",
                field_type="bool",
                required=False,
                description="Disable the SSH server hash check (set to true if server doesn't support it)"
            )
        ]

    def validate_config(self, config: dict) -> PluginResult:
        # Basic validation
        errors = []
        
        if not config.get('host'):
            errors.append("Host is required")
        
        if not config.get('user'):
            errors.append("Username is required")
        
        # Validate port if provided
        port = config.get('port', '22')
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                errors.append("Port must be between 1 and 65535")
        except ValueError:
            errors.append("Port must be a number")
        
        # If both password and key file are provided, that's OK
        # If neither is provided, that's also OK (will use SSH agent or prompt)
        
        if errors:
            return PluginResult(False, "; ".join(errors))
        
        return PluginResult(True, "Configuration appears valid")

    def test_connection(self, config: dict) -> PluginResult:
        # Create a temporary rclone config file with just this remote
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
            f.write(f"[test-remote]\n")
            f.write(f"type = sftp\n")
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
        result = {'type': 'sftp'}
        for key, value in config.items():
            if value:  # Only include non-empty values
                result[key] = value
        return result