#!/usr/bin/env python3
"""
Rclone GUI Manager - Simplified Single File Version
A simple GUI application for managing rclone remotes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import os
import subprocess
import sys
import json
import threading
from pathlib import Path

# Version - Update this manually for each release
VERSION = "1.0.6"

class RcloneManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Rclone GUI Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Application version
        self.version = VERSION
        
        # Load user preferences
        self.load_preferences()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Apply theme based on user preference
        if self.preferences.get('dark_mode', False):
            self.current_theme = 'dark'
        else:
            self.current_theme = 'light'
        
        # Initialize config path
        self.config_path = os.path.expanduser('~/.config/rclone/rclone.conf')
        
        # Initialize process tracking variables
        self.current_process = None
        self.current_operation = None
        
        # Load remotes
        self.load_remotes()
        
    def load_preferences(self):
        """Load user preferences from config file"""
        config_dir = Path.home() / '.config' / 'rclone-gui-manager'
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / 'preferences.json'
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.preferences = json.load(f)
            else:
                self.preferences = {'dark_mode': False}
        except Exception:
            self.preferences = {'dark_mode': False}
            
    def save_preferences(self):
        """Save user preferences to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")
            
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.preferences['dark_mode'] = True
        else:
            self.current_theme = 'light'
            self.preferences['dark_mode'] = False
            
        self.save_preferences()
        self.apply_theme()
        self.update_treeview_styles()
        
    def apply_theme(self):
        """Apply the current theme to the UI"""
        # Configure styles based on theme
        if self.current_theme == 'dark':
            # Dark theme colors
            self.style.configure('TFrame', background='#2d2d2d')
            self.style.configure('TLabel', background='#2d2d2d', foreground='white')
            self.style.configure('Header.TLabel', background='#2d2d2d', foreground='white', font=('Arial', 14, 'bold'))
            self.style.configure('Status.TLabel', background='#2d2d2d', foreground='white', font=('Arial', 10))
            
            # Button styling
            self.style.configure('TButton', background='#4d4d4d', foreground='white')
            self.style.map('TButton',
                          background=[('active', '#5d5d5d'), ('disabled', '#3d3d3d')],  # Darker when disabled
                          foreground=[('active', 'white'), ('disabled', '#888888')])   # Gray when disabled
            
            # Treeview styling
            self.style.configure('Treeview', 
                               background='#3d3d3d', 
                               foreground='white', 
                               fieldbackground='#3d3d3d')
            self.style.configure('Treeview.Heading', 
                               background='#4d4d4d', 
                               foreground='white')
                               
            # Update root background
            self.root.configure(bg='#2d2d2d')
            
            # Update icon colors for dark theme
            if hasattr(self, 'config_icon'):
                self.config_icon.config(bg='#2d2d2d', fg='#cccccc')
            if hasattr(self, 'settings_icon'):
                self.settings_icon.config(bg='#2d2d2d', fg='#cccccc')
        else:
            # Light theme colors
            self.style.configure('TFrame', background='#f0f0f0')
            self.style.configure('TLabel', background='#f0f0f0', foreground='black')
            self.style.configure('Header.TLabel', background='#f0f0f0', foreground='black', font=('Arial', 14, 'bold'))
            self.style.configure('Status.TLabel', background='#f0f0f0', foreground='black', font=('Arial', 10))
            
            # Button styling
            self.style.configure('TButton', background='#e1e1e1', foreground='black')
            self.style.map('TButton',
                          background=[('active', '#d1d1d1'), ('disabled', '#f0f0f0')],  # Lighter when disabled
                          foreground=[('active', 'black'), ('disabled', '#888888')])   # Gray when disabled
            
            # Treeview styling
            self.style.configure('Treeview', 
                               background='white', 
                               foreground='black', 
                               fieldbackground='white')
            self.style.configure('Treeview.Heading', 
                               background='#d0d0d0', 
                               foreground='black')
                               
            # Update root background
            self.root.configure(bg='#f0f0f0')
            
            # Update icon colors for light theme
            if hasattr(self, 'config_icon'):
                self.config_icon.config(bg='#f0f0f0', fg='#666666')
            if hasattr(self, 'settings_icon'):
                self.settings_icon.config(bg='#f0f0f0', fg='#666666')
            
        
    def update_treeview_styles(self):
        """Update treeview row styles based on mount status and theme"""
        # Configure treeview tags based on theme
        if self.current_theme == 'dark':
            self.tree.tag_configure('mounted', background='#2d4f2d')
        else:
            self.tree.tag_configure('mounted', background='#e0ffe0')
            
        # Update existing items to ensure they have the correct tags
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            values = item['values']
            if len(values) > 2 and values[2] == "Yes":  # Mounted column is at index 2
                self.tree.item(item_id, tags=('mounted',))
            else:
                self.tree.item(item_id, tags=())
                
    def edit_config_path(self):
        """Open file dialog to select rclone config file"""
        from tkinter import filedialog
        
        # Open file dialog to select config file
        new_path = filedialog.askopenfilename(
            title="Select rclone config file",
            initialdir=os.path.expanduser('~'),
            filetypes=[("Config files", "*.conf"), ("All files", "*.*")]
        )
        
        if new_path:
            self.config_path = new_path
            self.load_remotes()
            
    def on_icon_enter(self, event):
        """Handle mouse enter event for config icon"""
        if self.current_theme == 'dark':
            self.config_icon.config(fg="#ffffff")
        else:
            self.config_icon.config(fg="#000000")
            
    def on_icon_leave(self, event):
        """Handle mouse leave event for config icon"""
        if self.current_theme == 'dark':
            self.config_icon.config(fg="#cccccc")
        else:
            self.config_icon.config(fg="#666666")
            
    def on_settings_enter(self, event):
        """Handle mouse enter event for settings icon"""
        if self.current_theme == 'dark':
            self.settings_icon.config(fg="#ffffff")
        else:
            self.settings_icon.config(fg="#000000")
            
    def on_settings_leave(self, event):
        """Handle mouse leave event for settings icon"""
        if self.current_theme == 'dark':
            self.settings_icon.config(fg="#cccccc")
        else:
            self.settings_icon.config(fg="#666666")
            
    def open_changelog(self):
        """Open changelog in default web browser"""
        import webbrowser
        webbrowser.open("https://github.com/madroots/rclone-gui-manager/blob/main/CHANGELOG.md")
            
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header label
        self.header_label = ttk.Label(self.header_frame, text="Rclone Remote Manager", style='Header.TLabel')
        self.header_label.pack(side=tk.LEFT)
        
        # Gear icon for settings
        self.settings_icon = tk.Label(self.header_frame, text="⚙️", cursor="hand2", font=("Arial", 16), fg="#666666", bg='#f0f0f0')
        self.settings_icon.pack(side=tk.RIGHT)
        self.settings_icon.bind("<Button-1>", lambda e: self.open_settings_window())
        self.settings_icon.bind("<Enter>", self.on_settings_enter)
        self.settings_icon.bind("<Leave>", self.on_settings_leave)

        # Remove the theme button from main UI and keep it in settings only
        # self.theme_btn = ttk.Button(self.button_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        # self.theme_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, text="Ready", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        
        # Treeview for remotes
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('Remote', 'Type', 'Mounted', 'Cron', 'Mount Point')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        self.mount_btn = ttk.Button(self.button_frame, text="Mount", command=self.mount_selected)
        self.mount_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.unmount_btn = ttk.Button(self.button_frame, text="Unmount", command=self.unmount_selected)
        self.unmount_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.open_btn = ttk.Button(self.button_frame, text="Open Folder", command=self.open_selected, state=tk.DISABLED)
        self.open_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(self.button_frame, text="Refresh", command=self.refresh_remotes)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_btn = ttk.Button(self.button_frame, text="Test Connection", command=self.test_selected)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Cron frame
        self.cron_frame = ttk.Frame(self.main_frame)
        self.cron_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cron_var = tk.BooleanVar()
        self.cron_checkbox = ttk.Checkbutton(
            self.cron_frame, 
            text="Mount at startup (adds to crontab)", 
            variable=self.cron_var,
            command=self.toggle_cron
        )
        self.cron_checkbox.pack(side=tk.LEFT)

        # Version frame at the bottom
        self.version_frame = ttk.Frame(self.main_frame)
        self.version_frame.pack(fill=tk.X, pady=(5, 0))

        # Version label on the right side
        self.version_label = ttk.Label(self.version_frame, text=f"v{self.version}", font=('Arial', 8))
        self.version_label.pack(side=tk.RIGHT, padx=(0, 10))

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Initialize state
        self.selected_item = None
        
    def show_status(self, message, status_type='normal'):
        # Configure status label color based on theme and status type
        if self.current_theme == 'dark':
            if status_type == 'success':
                color = '#7fff7f'
            elif status_type == 'error':
                color = '#ff7f7f'
            elif status_type == 'warning':
                color = '#ffff7f'
            elif status_type == 'mounted':
                color = '#7fff7f'
            else:
                color = 'white'
        else:
            if status_type == 'success':
                color = 'green'
            elif status_type == 'error':
                color = 'red'
            elif status_type == 'warning':
                color = 'orange'
            elif status_type == 'mounted':
                color = 'green'
            else:
                color = 'black'
                
        self.style.configure('Status.TLabel', foreground=color)
        self.status_label.configure(text=message)
        
        # Reset status message after 5 seconds for non-error messages
        if status_type not in ['error']:
            if hasattr(self, 'status_reset_id'):
                self.root.after_cancel(self.status_reset_id)
            self.status_reset_id = self.root.after(5000, self.reset_status_message)
            
    def reset_status_message(self):
        """Reset the status message to the default state"""
        # Cancel any pending resets
        if hasattr(self, 'status_reset_id'):
            self.root.after_cancel(self.status_reset_id)
            delattr(self, 'status_reset_id')
            
        # Show the default status message based on the number of loaded remotes
        if hasattr(self, 'tree'):
            remote_count = len(self.tree.get_children())
            self.show_status(f"Loaded {remote_count} remotes", 'success')
        else:
            self.show_status("Ready", 'normal')
        
    def is_rclone_installed(self):
        """Check if rclone is installed and accessible"""
        try:
            result = subprocess.run(['rclone', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
            
    def show_progress(self, show=True, operation=""):
        # This method is kept for compatibility but doesn't do anything
        # since we removed the main progress bar
        pass
            
    def get_mount_dir(self, remote_name):
        """Get mount directory for a remote"""
        # Use ~/mnt for mount points to avoid permission issues
        home = Path.home()
        mount_base = home / "mnt"
        return mount_base / remote_name
        
    def create_mount_dir(self, remote_name):
        """Create mount directory if it doesn't exist"""
        mount_dir = self.get_mount_dir(remote_name)
        try:
            mount_dir.mkdir(parents=True, exist_ok=True)
            return str(mount_dir)
        except Exception as e:
            raise Exception(f"Failed to create mount directory {mount_dir}: {str(e)}")
            
    def is_mounted(self, mount_point):
        """Check if a directory is mounted"""
        try:
            result = subprocess.run(['mountpoint', '-q', mount_point], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            # If mountpoint command is not available, check with os.path.ismount
            return os.path.ismount(mount_point)
        except Exception:
            return False
            
    def load_remotes(self):
        """Load rclone remotes from config file"""
        self.show_progress(True)
        
        # Store the currently selected remote name to reselect it after refresh
        selected_remote_name = None
        if self.selected_item:
            try:
                item = self.tree.item(self.selected_item)
                selected_remote_name = item['values'][0]
            except:
                selected_remote_name = None
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Check if rclone is installed
        rclone_installed = self.is_rclone_installed()
        
        # Check if config file exists
        config_exists = os.path.exists(self.config_path)
        
        if not config_exists:
            if rclone_installed:
                self.show_status("Rclone detected but no config found. Use pencil icon to locate rclone.conf", 'warning')
            else:
                self.show_status("Rclone not detected. Install it or locate rclone.conf manually", 'error')
            self.show_progress(False)
            return
            
        # Config file exists
        config = configparser.ConfigParser()
        try:
            config.read(self.config_path)
        except Exception as e:
            self.show_status(f"Error reading config: {str(e)}", 'error')
            self.show_progress(False)
            return
            
        remotes = []
        for section in config.sections():
            remote_type = config.get(section, 'type', fallback='Unknown')
            mount_point = str(self.get_mount_dir(section))
            is_mounted = self.is_mounted(mount_point)
            mounted_text = "Yes" if is_mounted else "No"
            # Check if remote has cron setup
            has_cron = self.is_in_crontab(section)
            cron_text = "Yes" if has_cron else "No"
            remotes.append((section, remote_type, mounted_text, cron_text, mount_point))
            
        # Sort remotes by name
        remotes.sort(key=lambda x: x[0].lower())
        
        # Add to treeview
        for remote in remotes:
            # Apply 'mounted' tag if remote is mounted (index 2 is mounted column)
            is_mounted = remote[2] == "Yes"  # Check the "Mounted" column
            tags = ('mounted',) if is_mounted else ()
            item_id = self.tree.insert('', tk.END, values=remote, tags=tags)
            # If this is the previously selected remote, store its new item ID
            if selected_remote_name and remote[0] == selected_remote_name:
                self.selected_item = item_id
                
        # Show appropriate status message
        if rclone_installed:
            self.show_status(f"Loaded {len(remotes)} remotes", 'success')
        else:
            self.show_status(f"Rclone not detected but rclone.conf has been found and loaded {len(remotes)} remotes", 'warning')
            
        self.show_progress(False)
        
        # Update treeview styles
        self.update_treeview_styles()
        
        # Update button states
        self.update_button_states()
        
        # Re-select the item if it still exists
        if self.selected_item:
            try:
                self.tree.selection_set(self.selected_item)
            except:
                self.selected_item = None
                self.update_button_states()
        
    def refresh_remotes(self):
        """Refresh the remote list"""
        self.load_remotes()
        
    def on_select(self, event):
        """Handle treeview selection"""
        selection = self.tree.selection()
        if selection:
            self.selected_item = selection[0]
        else:
            self.selected_item = None
            
        # Update button states based on selection
        self.update_button_states()
        
        # Update cron checkbox state based on crontab
        self.update_cron_checkbox_state()
            
    def update_button_states(self):
        """Update button states based on selection and mount status"""
        # Reset button states
        self.mount_btn.configure(state=tk.NORMAL)
        self.unmount_btn.configure(state=tk.NORMAL)
        self.open_btn.configure(state=tk.DISABLED)
        
        # If no selection, disable all action buttons
        if not self.selected_item:
            self.mount_btn.configure(state=tk.DISABLED)
            self.unmount_btn.configure(state=tk.DISABLED)
            return
            
        # Get selected item data
        try:
            item = self.tree.item(self.selected_item)
            values = item['values']
        except:
            # If the item is no longer valid, reset selection
            self.selected_item = None
            self.mount_btn.configure(state=tk.DISABLED)
            self.unmount_btn.configure(state=tk.DISABLED)
            return
        
        if len(values) > 2:
            is_mounted = values[2] == "Yes"  # Mounted column is at index 2

            # Disable mount button if already mounted
            if is_mounted:
                self.mount_btn.configure(state=tk.DISABLED)
                self.open_btn.configure(state=tk.NORMAL)
            else:
                self.mount_btn.configure(state=tk.NORMAL)
                self.open_btn.configure(state=tk.DISABLED)

            # Disable unmount button if not mounted
            if not is_mounted:
                self.unmount_btn.configure(state=tk.DISABLED)
            else:
                self.unmount_btn.configure(state=tk.NORMAL)
                
    def update_cron_checkbox_state(self):
        """Update the cron checkbox state based on whether the selected remote is in crontab"""
        remote_name = self.get_selected_remote()
        if remote_name:
            self.cron_var.set(self.is_in_crontab(remote_name))
        else:
            # No selection, disable checkbox
            self.cron_var.set(False)
            
    def get_selected_remote(self):
        """Get the selected remote name"""
        if not self.selected_item:
            return None
            
        try:
            item = self.tree.item(self.selected_item)
            return item['values'][0]  # Remote name is first column
        except:
            return None
        
    def open_selected(self):
        """Open the mount folder for the selected remote"""
        if not self.selected_item:
            return

        try:
            item = self.tree.item(self.selected_item)
            values = item['values']
        except:
            return

        # Column indices: 0=Remote, 1=Type, 2=Mounted, 3=Cron, 4=Mount Point
        if len(values) > 4:
            mount_point = values[4]  # Mount Point is now at index 4
            try:
                # Try to open with xdg-open (Linux)
                subprocess.run(['xdg-open', mount_point], check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                try:
                    # Fallback to opening with file browser
                    subprocess.run(['gio', 'open', mount_point], check=True)
                except (subprocess.SubprocessError, FileNotFoundError):
                    # Show error message
                    self.show_status(f"Could not open {mount_point}", 'error')
                    messagebox.showerror("Error", f"Could not open folder: {mount_point}")
                    
    def test_connection(self, remote_name):
        """Test connection to remote"""
        try:
            # Store reference to the process for potential cancellation
            self.current_process = subprocess.Popen(['rclone', 'lsf', f'{remote_name}:'], 
                                                  stdout=subprocess.PIPE, 
                                                  stderr=subprocess.PIPE, 
                                                  text=True)
            self.current_operation = "test"
            
            # Wait for completion
            stdout, stderr = self.current_process.communicate(timeout=30)
            
            if self.current_process.returncode == 0:
                return True, "Connection successful"
            else:
                return False, f"Connection failed: {stderr}"
        except subprocess.TimeoutExpired:
            # Kill the process if it timed out
            if self.current_process:
                self.current_process.kill()
            return False, "Connection test timed out"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
        finally:
            # Clean up
            self.current_process = None
            self.current_operation = None
            
    def mount_remote(self, remote_name):
        """Mount remote"""
        try:
            # Create mount directory
            mount_point = self.create_mount_dir(remote_name)
            
            # Check if already mounted
            if self.is_mounted(mount_point):
                return True, f"{remote_name} is already mounted at {mount_point}"
            
            # Mount command
            cmd = ['rclone', 'mount', '--vfs-cache-mode', 'writes', 
                  f'{remote_name}:', mount_point]
            
            # Run mount in background
            self.current_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.PIPE)
            self.current_operation = "mount"
            
            # Give it a moment to see if it fails immediately
            try:
                self.current_process.wait(timeout=2)
                # If we get here, it failed to start
                stderr = self.current_process.stderr.read().decode() if self.current_process.stderr else ""
                return False, f"Mount failed: {stderr}"
            except subprocess.TimeoutExpired:
                # This is good - it means the mount is still running
                pass
                
            return True, f"Successfully mounted {remote_name} at {mount_point}"
            
        except Exception as e:
            return False, f"Mount failed: {str(e)}"
        finally:
            # Clean up
            self.current_process = None
            self.current_operation = None
            
    def unmount_remote(self, remote_name):
        """Unmount remote"""
        try:
            mount_point = str(self.get_mount_dir(remote_name))
            
            # Check if mounted
            if not self.is_mounted(mount_point):
                return True, f"{remote_name} is not mounted"
            
            # Try fusermount first (Linux)
            try:
                self.current_process = subprocess.Popen(['fusermount', '-u', mount_point], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE, 
                                              text=True)
                self.current_operation = "unmount"
                
                stdout, stderr = self.current_process.communicate()
                
                if self.current_process.returncode == 0:
                    return True, f"Successfully unmounted {remote_name}"
                else:
                    # Try umount as fallback
                    self.current_process = subprocess.Popen(['umount', mount_point], 
                                                  stdout=subprocess.PIPE, 
                                                  stderr=subprocess.PIPE, 
                                                  text=True)
                    self.current_operation = "unmount"
                    
                    stdout, stderr = self.current_process.communicate()
                    
                    if self.current_process.returncode == 0:
                        return True, f"Successfully unmounted {remote_name}"
                    else:
                        return False, f"Unmount failed: {stderr}"
            except FileNotFoundError:
                # Try umount directly
                self.current_process = subprocess.Popen(['umount', mount_point], 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE, 
                                              text=True)
                self.current_operation = "unmount"
                
                stdout, stderr = self.current_process.communicate()
                
                if self.current_process.returncode == 0:
                    return True, f"Successfully unmounted {remote_name}"
                else:
                    return False, f"Unmount failed: {stderr}"
        except Exception as e:
            return False, f"Unmount failed: {str(e)}"
        finally:
            # Clean up
            self.current_process = None
            self.current_operation = None
            
    def test_selected(self):
        """Test connection to selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            messagebox.showwarning("Warning", "Please select a remote to test")
            return
            
        # Show popup immediately
        self.show_operation_popup(f"Testing connection to {remote_name}")
        
        # Run the operation in a background thread
        thread = threading.Thread(target=self._run_test_connection, args=(remote_name,))
        thread.daemon = True
        thread.start()
        
    def _run_test_connection(self, remote_name):
        """Run the test connection operation in a background thread"""
        try:
            success, message = self.test_connection(remote_name)
            
            # Update UI in the main thread
            self.root.after(0, self._finish_test_connection, success, message)
        except Exception as e:
            self.root.after(0, self._finish_test_connection, False, f"Error: {str(e)}")
            
    def _finish_test_connection(self, success, message):
        """Finish the test connection operation in the main thread"""
        # Close popup if it exists
        if hasattr(self, 'operation_popup') and self.operation_popup:
            self.operation_popup.destroy()
            self.operation_popup = None
            
        # Update main UI
        self.show_progress(False)
        if success:
            self.show_status(message, 'success')
            messagebox.showinfo("Test Successful", message)
        else:
            self.show_status(message, 'error')
            messagebox.showerror("Test Failed", message)
            
    def mount_selected(self):
        """Mount selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            messagebox.showwarning("Warning", "Please select a remote to mount")
            return
            
        # Show popup immediately
        self.show_operation_popup(f"Mounting {remote_name}")
        
        # Run the operation in a background thread
        thread = threading.Thread(target=self._run_mount_remote, args=(remote_name,))
        thread.daemon = True
        thread.start()
        
    def _run_mount_remote(self, remote_name):
        """Run the mount remote operation in a background thread"""
        try:
            # Test connection first
            success, message = self.test_connection(remote_name)
            if not success:
                self.root.after(0, self._finish_mount_remote, False, 
                               f"Cannot mount {remote_name} - connection test failed:\n{message}")
                return
                
            # Proceed with mount
            success, message = self.mount_remote(remote_name)
            
            # Update UI in the main thread
            self.root.after(0, self._finish_mount_remote, success, message)
        except Exception as e:
            self.root.after(0, self._finish_mount_remote, False, f"Error: {str(e)}")
            
    def _finish_mount_remote(self, success, message):
        """Finish the mount remote operation in the main thread"""
        # Close popup if it exists
        if hasattr(self, 'operation_popup') and self.operation_popup:
            self.operation_popup.destroy()
            self.operation_popup = None
            
        # Update main UI
        self.show_progress(False)
        if success:
            self.show_status(message, 'success')
            messagebox.showinfo("Mount Successful", message)
            self.refresh_remotes()
        else:
            self.show_status(message, 'error')
            messagebox.showerror("Mount Failed", message)
            
    def unmount_selected(self):
        """Unmount selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            messagebox.showwarning("Warning", "Please select a remote to unmount")
            return
            
    def unmount_selected(self):
        """Unmount selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            messagebox.showwarning("Warning", "Please select a remote to unmount")
            return
            
        # Show popup immediately
        self.show_operation_popup(f"Unmounting {remote_name}")
        
        # Run the operation in a background thread
        thread = threading.Thread(target=self._run_unmount_remote, args=(remote_name,))
        thread.daemon = True
        thread.start()
        
    def _run_unmount_remote(self, remote_name):
        """Run the unmount remote operation in a background thread"""
        try:
            success, message = self.unmount_remote(remote_name)
            
            # Update UI in the main thread
            self.root.after(0, self._finish_unmount_remote, success, message)
        except Exception as e:
            self.root.after(0, self._finish_unmount_remote, False, f"Error: {str(e)}")
            
    def _finish_unmount_remote(self, success, message):
        """Finish the unmount remote operation in the main thread"""
        # Close popup if it exists
        if hasattr(self, 'operation_popup') and self.operation_popup:
            self.operation_popup.destroy()
            self.operation_popup = None
            
        # Update main UI
        self.show_progress(False)
        if success:
            self.show_status(message, 'success')
            messagebox.showinfo("Unmount Successful", message)
            self.refresh_remotes()
        else:
            self.show_status(message, 'error')
            messagebox.showerror("Unmount Failed", message)
            
    def is_in_crontab(self, remote_name):
        """Check if a remote is already in crontab"""
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                return False
                
            current_cron = result.stdout
            mount_cmd = f"rclone mount --vfs-cache-mode writes {remote_name}:"
            return mount_cmd in current_cron
        except Exception:
            return False
            
    def kill_operation(self):
        """Kill the currently running operation"""
        if self.current_process and self.current_process.poll() is None:
            # Process is still running
            try:
                self.current_process.kill()
                self.current_process.wait(timeout=5)  # Wait for process to terminate
                self.show_status("Operation killed by user", 'warning')
                messagebox.showinfo("Operation Killed", "The operation has been terminated.")
            except subprocess.TimeoutExpired:
                # Process didn't terminate in time
                self.show_status("Failed to kill operation", 'error')
                messagebox.showerror("Kill Failed", "Failed to terminate the operation. It may still be running.")
            except Exception as e:
                self.show_status(f"Error killing operation: {str(e)}", 'error')
                messagebox.showerror("Kill Error", f"An error occurred while trying to kill the operation: {str(e)}")
        else:
            self.show_status("No operation to kill", 'warning')
            
    def show_operation_popup(self, operation_name):
        """Show a popup window for long-running operations with a kill button"""
        # Create a new top-level window
        self.popup = tk.Toplevel(self.root)
        self.popup.title(f"{operation_name} in progress")
        self.popup.geometry("300x150")
        self.popup.resizable(False, False)
        
        # Apply theme to popup
        if self.current_theme == 'dark':
            self.popup.configure(bg='#2d2d2d')
        else:
            self.popup.configure(bg='#f0f0f0')
        
        # Center the popup window
        self.popup.transient(self.root)
        self.popup.grab_set()
        
        # Add label
        label = ttk.Label(self.popup, text=f"{operation_name} in progress...", style='Status.TLabel')
        label.pack(pady=20)
        
        # Add progress bar
        progress = ttk.Progressbar(self.popup, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=10)
        progress.start(10)
        
        # Add kill button
        kill_btn = ttk.Button(self.popup, text="Kill Operation", command=self.kill_operation_from_popup)
        kill_btn.pack(pady=10)
        
        # Store reference to popup
        self.operation_popup = self.popup
        
    def kill_operation_from_popup(self):
        """Kill the current operation from the popup window"""
        self.kill_operation()
        if hasattr(self, 'operation_popup') and self.operation_popup:
            self.operation_popup.destroy()
            self.operation_popup = None
            
    def toggle_cron(self):
        """Toggle cron entry for selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            self.cron_var.set(False)
            messagebox.showwarning("Warning", "Please select a remote first")
            return
            
        if self.cron_var.get():
            # Check if already in crontab before adding
            if self.is_in_crontab(remote_name):
                self.show_status("Remote already in crontab", 'warning')
                messagebox.showinfo("Info", f"Remote '{remote_name}' is already scheduled for auto-mount at startup.")
                # Update checkbox state to match actual status
                self.update_cron_checkbox_state()
                return
            self.add_to_cron(remote_name)
        else:
            self.remove_from_cron(remote_name)
            
    def add_to_cron(self, remote_name):
        """Add mount command to crontab"""
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout
            
            # Check if entry already exists
            mount_cmd = f"rclone mount --vfs-cache-mode writes {remote_name}:"
            if mount_cmd in current_cron:
                self.show_status("Cron entry already exists", 'warning')
                messagebox.showinfo("Info", f"Remote '{remote_name}' is already scheduled for auto-mount at startup.")
                return
                
            # Add new entry
            new_entry = f"@reboot {mount_cmd} {self.get_mount_dir(remote_name)}\n"
            new_cron = current_cron + new_entry
            
            # Write to crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            _, stderr = process.communicate(input=new_cron.encode())
            
            if process.returncode == 0:
                self.show_status(f"Added {remote_name} to crontab for auto-mount", 'success')
                # Refresh the remote list to show cron indicator
                self.load_remotes()
            else:
                self.cron_var.set(False)
                self.show_status(f"Failed to add to crontab: {stderr.decode()}", 'error')
                
        except Exception as e:
            self.cron_var.set(False)
            self.show_status(f"Cron operation failed: {str(e)}", 'error')
            
    def remove_from_cron(self, remote_name):
        """Remove mount command from crontab"""
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                self.show_status("No crontab entries found", 'warning')
                return
                
            current_cron = result.stdout
            mount_cmd = f"rclone mount --vfs-cache-mode writes {remote_name}:"
            
            # Filter out entries with this remote
            lines = current_cron.splitlines()
            new_lines = [line for line in lines if mount_cmd not in line]
            new_cron = "\n".join(new_lines) + ("\n" if new_lines else "")
            
            # Write to crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            _, stderr = process.communicate(input=new_cron.encode())
            
            if process.returncode == 0:
                self.show_status(f"Removed {remote_name} from crontab", 'success')
                # Refresh the remote list to remove cron indicator
                self.load_remotes()
            else:
                self.show_status(f"Failed to remove from crontab: {stderr.decode()}", 'error')
                
        except Exception as e:
            self.show_status(f"Cron operation failed: {str(e)}", 'error')

    def open_settings_window(self):
        """Open the settings window"""
        # Create a new top-level window
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x300")
        self.settings_window.resizable(False, False)

        # Apply theme to settings window
        if self.current_theme == 'dark':
            self.settings_window.configure(bg='#2d2d2d')
        else:
            self.settings_window.configure(bg='#f0f0f0')

        # Center the settings window
        self.settings_window.transient(self.root)
        # self.settings_window.grab_set()  # Commenting out due to viewability issue

        # Add label
        label = ttk.Label(self.settings_window, text="Application Settings", font=('Arial', 14, 'bold'))
        label.pack(pady=20)

        # Theme selection frame
        theme_frame = ttk.Frame(self.settings_window)
        theme_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(theme_frame, text="Theme:").pack(anchor=tk.W)

        # Theme selection
        self.theme_var = tk.StringVar(value="Dark" if self.current_theme == 'dark' else "Light")
        theme_radio_frame = ttk.Frame(theme_frame)
        theme_radio_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(theme_radio_frame, text="Light", variable=self.theme_var, value="Light").pack(side=tk.LEFT)
        ttk.Radiobutton(theme_radio_frame, text="Dark", variable=self.theme_var, value="Dark").pack(side=tk.LEFT, padx=(10, 0))

        # Config path frame
        config_frame = ttk.Frame(self.settings_window)
        config_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(config_frame, text="Rclone Config Path:").pack(anchor=tk.W)

        # Config path entry
        self.config_path_var = tk.StringVar(value=self.config_path)
        config_entry_frame = ttk.Frame(config_frame)
        config_entry_frame.pack(fill=tk.X, pady=5)

        self.config_path_entry = ttk.Entry(config_entry_frame, textvariable=self.config_path_var)
        self.config_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        config_path_btn = ttk.Button(config_entry_frame, text="Browse", command=self.browse_config_path)
        config_path_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Buttons frame
        button_frame = ttk.Frame(self.settings_window)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        # OK and Cancel buttons
        ok_btn = ttk.Button(button_frame, text="OK", command=self.save_settings)
        ok_btn.pack(side=tk.RIGHT, padx=(5, 0))

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)


    def browse_config_path(self):
        """Browse for rclone config file"""
        from tkinter import filedialog

        # Open file dialog to select config file
        new_path = filedialog.askopenfilename(
            title="Select rclone config file",
            initialdir=os.path.expanduser('~'),
            filetypes=[("Config files", "*.conf"), ("All files", "*.*")]
        )

        if new_path:
            self.config_path_var.set(new_path)

    def save_settings(self):
        """Save settings and close window"""
        # Update theme if changed
        new_theme = self.theme_var.get().lower()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.preferences['dark_mode'] = (new_theme == 'dark')
            self.save_preferences()
            self.apply_theme()
            self.update_treeview_styles()

        # Update config path if changed
        new_config_path = self.config_path_var.get()
        if new_config_path and new_config_path != self.config_path:
            self.config_path = new_config_path
            self.load_remotes()

        # Close settings window
        self.settings_window.destroy()


def main():
    root = tk.Tk()
    app = RcloneManager(root)
    # Apply initial theme
    app.apply_theme()
    root.mainloop()


if __name__ == "__main__":
    main()