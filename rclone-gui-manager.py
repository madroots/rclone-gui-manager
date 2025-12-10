#!/usr/bin/env python3
"""
Rclone GUI Manager - Simplified Single File Version
A simple GUI application for managing rclone remotes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
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

        # Initialize plugin manager
        self.init_plugin_manager()

        # Load remotes
        self.load_remotes()
        
    def init_plugin_manager(self):
        """Initialize the plugin manager"""
        try:
            from plugins.plugin_manager import PluginManager
            self.plugin_manager = PluginManager()
            self.plugin_manager.load_plugins()
        except ImportError:
            # If plugins module is not available, create a minimal mock
            self.plugin_manager = None

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
            # Update delete button for dark theme - match the style of other buttons
            if hasattr(self, 'delete_remote_btn'):
                # Use the same colors as disabled buttons initially
                self.delete_remote_btn.configure(
                    bg='#4d4d4d',  # Same as other buttons in dark theme
                    fg='#888888',  # Gray when disabled/inactive
                    activebackground='#5d5d5d',
                    activeforeground='#888888'  # Gray when active but disabled
                )
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
            # Update delete button for light theme - match the style of other buttons
            if hasattr(self, 'delete_remote_btn'):
                # Use the same colors as disabled buttons initially
                self.delete_remote_btn.configure(
                    bg='#e1e1e1',  # Same as other buttons in light theme
                    fg='#888888',  # Gray when disabled/inactive
                    activebackground='#d1d1d1',
                    activeforeground='#888888'  # Gray when active but disabled
                )
            
        
    def update_treeview_styles(self):
        """Update treeview row styles based on mount status and theme"""
        # Configure treeview tags based on theme
        if self.current_theme == 'dark':
            self.tree.tag_configure('mounted', background='#2d4f2d')
            self.tree.tag_configure('add_new', background='#3a3a5a', foreground='#8ab4f8')  # Softer blue for dark theme
        else:
            self.tree.tag_configure('mounted', background='#e0ffe0')
            self.tree.tag_configure('add_new', background='#e6e6fa', foreground='#5b78c7')  # Softer blue for light theme

        # Update existing items to ensure they have the correct tags
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            values = item['values']
            if values and len(values) > 0 and values[0] == '+ Add New Remote':
                # This is the 'Add New Remote' item
                self.tree.item(item_id, tags=('add_new',))
            elif len(values) > 2 and values[2] == "Yes":  # Mounted column is at index 2
                self.tree.item(item_id, tags=('mounted',))
            else:
                # For regular remotes that are not mounted
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

        self.edit_remote_btn = ttk.Button(self.button_frame, text="Edit Remote", command=self.edit_selected_remote, state=tk.DISABLED)
        self.edit_remote_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Create a delete button with a trash icon
        self.delete_remote_btn = tk.Button(
            self.button_frame,
            text="🗑",  # Trash icon
            command=self.delete_selected_remote,
            state=tk.DISABLED,
            width=3,
            cursor='hand2',
            font=('Arial', 10, 'bold')
        )
        # Style the delete button to match other buttons - will be updated when theme is applied
        # Initially set to disabled state colors
        self.delete_remote_btn.configure(
            relief='flat',
            borderwidth=1,
            padx=5,
            pady=2
        )
        # Apply initial theme-appropriate styling
        if self.preferences.get('dark_mode', False):
            self.delete_remote_btn.configure(
                bg='#4d4d4d',  # Dark button background
                fg='#888888',  # Gray text when disabled
                activebackground='#5d5d5d',
                activeforeground='#888888'  # Gray when active but disabled
            )
        else:
            self.delete_remote_btn.configure(
                bg='#e1e1e1',  # Light button background
                fg='#888888',  # Gray text when disabled
                activebackground='#d1d1d1',
                activeforeground='#888888'  # Gray when active but disabled
            )
        self.delete_remote_btn.pack(side=tk.RIGHT, padx=(5, 0))

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
                if item and 'values' in item and item['values']:
                    # Check if this is the 'Add New Remote' item
                    if len(item['values']) > 0 and item['values'][0] == '+ Add New Remote':
                        selected_remote_name = '+ Add New Remote'
                    else:
                        selected_remote_name = item['values'][0]
            except:
                selected_remote_name = None

        # Clear existing items
        for item in self.tree.get_children():
            # Don't delete the 'Add New Remote' item if it exists, we'll add it back at the end
            if self.tree.item(item, 'values') and self.tree.item(item, 'values')[0] != '+ Add New Remote':
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
            # Add the 'Add New Remote' item even when config doesn't exist
            self.tree.insert('', tk.END, values=('+ Add New Remote', '', '', '', ''), tags=('add_new',))
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

        # Add the 'Add New Remote' item as the last item
        add_new_item_id = self.tree.insert('', tk.END, values=('+ Add New Remote', '', '', '', ''), tags=('add_new',))

        # If the 'Add New Remote' was previously selected, select it again
        if selected_remote_name == '+ Add New Remote':
            self.selected_item = add_new_item_id

        # Update the style for the 'Add New' item
        self.style.configure('AddNew.TLabel', foreground='blue')

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
        """Refresh the remote list and reload plugins"""
        # Reload plugins to check for any new ones
        if self.plugin_manager:
            self.plugin_manager.load_plugins()
        self.load_remotes()
        
    def on_select(self, event):
        """Handle treeview selection"""
        selection = self.tree.selection()
        if selection:
            self.selected_item = selection[0]

            # Check if the selected item is the 'Add New Remote' item
            item_values = self.tree.item(self.selected_item, 'values')
            if item_values and len(item_values) > 0 and item_values[0] == '+ Add New Remote':
                # Use after_idle to ensure the event processing completes before opening the dialog
                self.root.after_idle(self._handle_add_new_remote)
                return  # Don't update button states until after we handle the add new remote
        else:
            self.selected_item = None

        # Update button states based on selection
        self.update_button_states()

        # Update cron checkbox state based on crontab
        self.update_cron_checkbox_state()

    def _handle_add_new_remote(self):
        """Handle adding a new remote after selection event completes"""
        # Temporarily clear selection to avoid conflicts
        self.tree.selection_remove(self.selected_item)
        self.selected_item = None

        # Now open the add new remote dialog
        self.add_new_remote()

        # After the dialog is opened, update button states
        self.update_button_states()
            
    def update_button_states(self):
        """Update button states based on selection and mount status"""
        # Reset button states
        self.mount_btn.configure(state=tk.NORMAL)
        self.unmount_btn.configure(state=tk.NORMAL)
        self.open_btn.configure(state=tk.DISABLED)
        self.edit_remote_btn.configure(state=tk.NORMAL)
        self.delete_remote_btn.configure(state=tk.NORMAL)

        # If no selection, disable all action buttons
        if not self.selected_item:
            self.mount_btn.configure(state=tk.DISABLED)
            self.unmount_btn.configure(state=tk.DISABLED)
            self.edit_remote_btn.configure(state=tk.DISABLED)
            self.delete_remote_btn.configure(state=tk.DISABLED)
            # Change delete button text color to gray when disabled
            if self.current_theme == 'dark':
                self.delete_remote_btn.configure(fg='#888888')  # Gray for dark theme
            else:
                self.delete_remote_btn.configure(fg='#888888')  # Gray for light theme
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
            self.edit_remote_btn.configure(state=tk.DISABLED)
            self.delete_remote_btn.configure(state=tk.DISABLED)
            return

        # Check if the selected item is the 'Add New Remote' item
        if values and len(values) > 0 and values[0] == '+ Add New Remote':
            # Disable all action buttons for the 'Add New Remote' item
            self.mount_btn.configure(state=tk.DISABLED)
            self.unmount_btn.configure(state=tk.DISABLED)
            self.open_btn.configure(state=tk.DISABLED)
            self.edit_remote_btn.configure(state=tk.DISABLED)
            self.delete_remote_btn.configure(state=tk.DISABLED)
            # Change delete button text color to gray when disabled
            if self.current_theme == 'dark':
                self.delete_remote_btn.configure(fg='#888888')  # Gray for dark theme
            else:
                self.delete_remote_btn.configure(fg='#888888')  # Gray for light theme
            return

        if len(values) > 2:
            is_mounted = values[2] == "Yes"  # Mounted column is at index 2
            remote_name = values[0]  # Remote name is first column
            remote_type = values[1]  # Remote type is second column

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

            # Check if there's a plugin available for this remote type
            # We'll check by looking for a plugin that matches the remote type
            has_plugin = self._has_plugin_for_type(remote_type)
            if not has_plugin:
                self.edit_remote_btn.configure(state=tk.DISABLED)
            else:
                self.edit_remote_btn.configure(state=tk.NORMAL)

        # Set the delete button to enabled state - only change the icon color to red
        if self.current_theme == 'dark':
            self.delete_remote_btn.configure(fg='red')  # Red icon for dark theme when enabled
        else:
            self.delete_remote_btn.configure(fg='red')  # Red icon for light theme when enabled


    def _has_plugin_for_type(self, remote_type):
        """Check if there's a plugin available for a specific remote type"""
        if not self.plugin_manager:
            return False

        # Find a plugin that can handle this remote type
        for plugin_name in self.plugin_manager.get_available_plugins():
            plugin = self.plugin_manager.get_plugin(plugin_name)
            # Check if the plugin name matches the remote type or if it has a standard type
            if plugin.get_name().lower() == remote_type.lower():
                return True

        # Special case: if remote_type is 'sftp' and we have sftp plugin
        # We need to check this differently since plugin names may not exactly match remote types
        for plugin_name in self.plugin_manager.get_available_plugins():
            plugin = self.plugin_manager.get_plugin(plugin_name)
            # Check if there's a plugin that can handle this remote type
            # For example, if we're loading existing remotes, we should match based on type
            # For now, we'll check if the plugin name contains the remote type
            if remote_type.lower() in plugin.get_name().lower() or plugin.get_name().lower() in remote_type.lower():
                return True

        return False
                
    def update_cron_checkbox_state(self):
        """Update the cron checkbox state based on whether the selected remote is in crontab"""
        remote_name = self.get_selected_remote()
        if remote_name:
            self.cron_var.set(self.is_in_crontab(remote_name))
        else:
            # No selection, disable checkbox
            self.cron_var.set(False)

    def edit_selected_remote(self):
        """Edit the selected remote if a plugin is available for its type"""
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select a remote to edit")
            return

        try:
            item = self.tree.item(self.selected_item)
            remote_name = item['values'][0]  # Remote name is first column
            remote_type = item['values'][1]  # Remote type is second column
        except:
            messagebox.showerror("Error", "Could not get remote details")
            return

        # Check if there's a plugin available for this remote type
        plugin = self._get_plugin_for_type(remote_type)
        if not plugin:
            messagebox.showinfo("Not Editable", f"Remote '{remote_name}' of type '{remote_type}' is not editable because no plugin is available for this type.")
            return

        # Get the current configuration for this remote
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)

            if remote_name in config:
                remote_config = dict(config[remote_name])
                # Remove the 'type' key since we don't need it in the form values
                if 'type' in remote_config:
                    del remote_config['type']
            else:
                messagebox.showerror("Error", f"Remote '{remote_name}' not found in config")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Could not read remote configuration: {str(e)}")
            return

        # Open the configuration form with existing values
        self.open_remote_config_form_for_edit(plugin, remote_name, remote_config)

    def _get_plugin_for_type(self, remote_type):
        """Get the plugin that can handle a specific remote type"""
        if not self.plugin_manager:
            return None

        # Find a plugin that can handle this remote type
        for plugin_name in self.plugin_manager.get_available_plugins():
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if plugin.get_name().lower() == remote_type.lower():
                return plugin

        return None

    def open_remote_config_form_for_edit(self, plugin, remote_name, existing_config):
        """Open the configuration form for editing an existing remote"""
        # Create new window for remote configuration
        config_window = tk.Toplevel(self.root)
        config_window.title(f"Edit {remote_name} ({plugin.get_name()})")
        config_window.geometry("500x600")
        config_window.resizable(True, True)

        # Apply theme to config window
        if self.current_theme == 'dark':
            config_window.configure(bg='#2d2d2d')
        else:
            config_window.configure(bg='#f0f0f0')

        # Center the config window
        config_window.transient(self.root)
        # config_window.grab_set()  # Commented out to avoid conflicts

        # Create a scrollable frame
        main_frame = ttk.Frame(config_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add description if available
        description = plugin.get_description()
        if description:
            desc_label = ttk.Label(scrollable_frame, text=description, wraplength=450)
            desc_label.pack(fill=tk.X, pady=(0, 10))

        # Add notes if available
        notes = plugin.get_notes()
        if notes:
            notes_frame = ttk.LabelFrame(scrollable_frame, text="Notes", padding=(10, 5))
            notes_frame.pack(fill=tk.X, pady=(0, 10))

            notes_label = ttk.Label(notes_frame, text=notes, wraplength=430)
            notes_label.pack(fill=tk.X)

        # Store configuration values
        config_vars = {}

        # Create the name field first (disabled since it can't be changed)
        name_field_frame = ttk.Frame(scrollable_frame)
        name_field_frame.pack(fill=tk.X, pady=5)

        name_label = ttk.Label(name_field_frame, text="Remote Name:")
        name_label.pack(anchor=tk.W)

        name_var = tk.StringVar(value=remote_name)
        config_vars['remote_name'] = name_var
        name_entry = ttk.Entry(name_field_frame, textvariable=name_var, state='readonly')
        name_entry.pack(fill=tk.X)
        name_entry.configure(state='readonly')  # Make it read-only

        name_desc_label = ttk.Label(name_field_frame, text="Remote name cannot be changed", font=('Arial', 8))
        name_desc_label.pack(anchor=tk.W)

        # Get fields from plugin
        fields = plugin.get_fields()

        # Create UI elements for each field
        for field in fields:
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill=tk.X, pady=5)

            label = ttk.Label(field_frame, text=f"{field.label}{' *' if field.required else ''}:")
            label.pack(anchor=tk.W)

            # Get the existing value for this field from the config
            existing_value = existing_config.get(field.name, field.default)

            if field.field_type == "bool":
                # Boolean field (checkbox)
                var = tk.BooleanVar(value=existing_value.lower() in ['true', '1', 'yes'] if existing_value else False)
                config_vars[field.name] = var
                checkbox = ttk.Checkbutton(field_frame, variable=var, text="")
                checkbox.pack(fill=tk.X)

                # Set the initial state based on the existing value
                checkbox.state(['!alternate'])  # Ensure it's not in indeterminate state
                if existing_value.lower() in ['true', '1', 'yes'] if existing_value else False:
                    var.set(True)
                else:
                    var.set(False)

            elif field.field_type == "choice":
                # Choice field (combobox)
                var = tk.StringVar(value=existing_value)
                config_vars[field.name] = var
                combobox = ttk.Combobox(field_frame, textvariable=var, values=field.choices, state="readonly")
                combobox.pack(fill=tk.X)
                if existing_value:
                    combobox.set(existing_value)
            elif field.field_type == "file":
                # File field with browse button
                var = tk.StringVar(value=existing_value)
                config_vars[field.name] = var

                file_frame = ttk.Frame(field_frame)
                file_frame.pack(fill=tk.X, pady=2)

                entry = ttk.Entry(file_frame, textvariable=var)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                browse_btn = ttk.Button(file_frame, text="Browse", command=lambda v=var, f=field: self._browse_file(v, f))
                browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
            elif field.field_type == "password":
                # Password field
                var = tk.StringVar(value=existing_value)
                config_vars[field.name] = var
                entry = ttk.Entry(field_frame, textvariable=var, show="*")
                entry.pack(fill=tk.X)
            elif field.field_type in ["int", "float"]:
                # Number field
                var = tk.StringVar(value=existing_value)
                config_vars[field.name] = var
                entry = ttk.Entry(field_frame, textvariable=var)
                entry.pack(fill=tk.X)
            else:
                # Text field
                var = tk.StringVar(value=existing_value)
                config_vars[field.name] = var
                entry = ttk.Entry(field_frame, textvariable=var)
                entry.pack(fill=tk.X)

            # Add description if available
            if field.description:
                desc_label = ttk.Label(field_frame, text=field.description, font=('Arial', 8))
                desc_label.pack(anchor=tk.W)

        # Add advanced fields if available
        advanced_fields = plugin.get_advanced_fields()
        if advanced_fields:
            advanced_frame = ttk.LabelFrame(scrollable_frame, text="Advanced Options", padding=(10, 5))
            advanced_frame.pack(fill=tk.X, pady=(10, 0))

            for field in advanced_fields:
                field_frame = ttk.Frame(advanced_frame)
                field_frame.pack(fill=tk.X, pady=5)

                label = ttk.Label(field_frame, text=f"{field.label}{' *' if field.required else ''}:")
                label.pack(anchor=tk.W)

                # Get the existing value for this field from the config
                existing_value = existing_config.get(field.name, field.default)

                if field.field_type == "bool":
                    var = tk.BooleanVar(value=existing_value.lower() in ['true', '1', 'yes'] if existing_value else False)
                    config_vars[field.name] = var
                    checkbox = ttk.Checkbutton(field_frame, variable=var, text="")
                    checkbox.pack(fill=tk.X)

                    # Set the initial state based on the existing value
                    checkbox.state(['!alternate'])
                    if existing_value.lower() in ['true', '1', 'yes'] if existing_value else False:
                        var.set(True)
                    else:
                        var.set(False)

                elif field.field_type == "choice":
                    var = tk.StringVar(value=existing_value)
                    config_vars[field.name] = var
                    combobox = ttk.Combobox(field_frame, textvariable=var, values=field.choices, state="readonly")
                    combobox.pack(fill=tk.X)
                    if existing_value:
                        combobox.set(existing_value)
                elif field.field_type == "file":
                    var = tk.StringVar(value=existing_value)
                    config_vars[field.name] = var

                    file_frame = ttk.Frame(field_frame)
                    file_frame.pack(fill=tk.X, pady=2)

                    entry = ttk.Entry(file_frame, textvariable=var)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    browse_btn = ttk.Button(file_frame, text="Browse", command=lambda v=var, f=field: self._browse_file(v, f))
                    browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
                elif field.field_type == "password":
                    var = tk.StringVar(value=existing_value)
                    config_vars[field.name] = var
                    entry = ttk.Entry(field_frame, textvariable=var, show="*")
                    entry.pack(fill=tk.X)
                elif field.field_type in ["int", "float"]:
                    var = tk.StringVar(value=existing_value)
                    config_vars[field.name] = var
                    entry = ttk.Entry(field_frame, textvariable=var)
                    entry.pack(fill=tk.X)
                else:
                    var = tk.StringVar(value=existing_value)
                    config_vars[field.name] = var
                    entry = ttk.Entry(field_frame, textvariable=var)
                    entry.pack(fill=tk.X)

                # Add description if available
                if field.description:
                    desc_label = ttk.Label(field_frame, text=field.description, font=('Arial', 8))
                    desc_label.pack(anchor=tk.W)

        # Add buttons frame
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        def test_connection():
            # Collect configuration values
            config_data = {}
            for name, var in config_vars.items():
                if name != 'remote_name':  # Skip the remote name field
                    value = var.get()
                    if isinstance(value, bool):
                        config_data[name] = str(value).lower()
                    else:
                        config_data[name] = str(value) if value else ""

            # Validate configuration
            validation = plugin.validate_config(config_data)
            if not validation.success:
                messagebox.showerror("Validation Error", validation.message)
                return

            # Test connection
            test_result = plugin.test_connection(config_data)
            if test_result.success:
                messagebox.showinfo("Test Successful", test_result.message)
            else:
                messagebox.showerror("Test Failed", test_result.message)

        def save_remote():
            # Collect configuration values
            config_data = {}
            for name, var in config_vars.items():
                if name != 'remote_name':  # Skip the remote name field
                    value = var.get()
                    if isinstance(value, bool):
                        config_data[name] = str(value).lower()
                    else:
                        config_data[name] = str(value) if value else ""

            # Validate configuration
            validation = plugin.validate_config(config_data)
            if not validation.success:
                messagebox.showerror("Validation Error", validation.message)
                return

            # Get the remote name (unchanged from original)
            remote_name = config_vars['remote_name'].get()
            if not remote_name:
                messagebox.showerror("Error", "Remote name is required")
                return

            # Check if user wants to save even with errors
            test_result = plugin.test_connection(config_data)
            if not test_result.success:
                response = messagebox.askyesno(
                    "Configuration Not Working",
                    f"Connection test failed: {test_result.message}\n\n"
                    f"Do you still want to save this configuration?",
                    icon='warning'
                )
                if not response:
                    return

            # Update the rclone config with new values
            self.update_remote_config(remote_name, plugin, config_data, config_window)

        # Add test, save and cancel buttons
        test_btn = ttk.Button(button_frame, text="Test Connection", command=test_connection)
        test_btn.pack(side=tk.RIGHT, padx=(5, 0))

        save_btn = ttk.Button(button_frame, text="Save", command=save_remote)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=config_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)

        # Add scrollbar to canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_remote_config(self, remote_name, plugin, config_data, window):
        """Update an existing remote configuration in rclone.conf"""
        try:
            # Read the existing config file
            if not os.path.exists(self.config_path):
                messagebox.showerror("Error", "Rclone config file does not exist")
                return

            config = configparser.ConfigParser()
            config.read(self.config_path)

            # Check if remote exists
            if remote_name not in config:
                messagebox.showerror("Error", f"Remote '{remote_name}' does not exist in config")
                return

            # Get the remote type from the existing config
            remote_type = config.get(remote_name, 'type', fallback='Unknown')

            # Clear existing options for this remote (except type)
            for option in config.options(remote_name):
                if option.lower() != 'type':  # Keep the type field
                    config.remove_option(remote_name, option)

            # Add the updated configuration values
            config_format = plugin.get_config_format(config_data)
            for key, value in config_format.items():
                if key != 'type':  # Type is already set and shouldn't be overridden
                    config.set(remote_name, key, str(value))

            # Write the config back to the file
            with open(self.config_path, 'w') as f:
                config.write(f)

            # Show success message
            messagebox.showinfo("Success", f"Remote '{remote_name}' has been updated successfully!")

            # Close the configuration window
            window.destroy()

            # Refresh the remotes list
            self.load_remotes()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update remote: {str(e)}")

    def delete_selected_remote(self):
        """Delete the selected remote from rclone config"""
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select a remote to delete")
            return

        try:
            item = self.tree.item(self.selected_item)
            remote_name = item['values'][0]  # Remote name is first column
        except:
            messagebox.showerror("Error", "Could not get remote details")
            return

        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete the remote '{remote_name}'?\n\n"
            f"This will remove it from your rclone configuration file and cannot be undone.",
            icon='warning'
        )

        if not result:
            return

        # Delete the remote
        self.remove_remote_config(remote_name)

    def remove_remote_config(self, remote_name):
        """Remove a remote from rclone.conf"""
        try:
            # Read the existing config file
            if not os.path.exists(self.config_path):
                messagebox.showerror("Error", "Rclone config file does not exist")
                return

            config = configparser.ConfigParser()
            config.read(self.config_path)

            # Check if remote exists
            if remote_name not in config:
                messagebox.showerror("Error", f"Remote '{remote_name}' does not exist in config")
                return

            # Remove the section for this remote
            config.remove_section(remote_name)

            # Write the config back to the file
            with open(self.config_path, 'w') as f:
                config.write(f)

            # Show success message
            messagebox.showinfo("Success", f"Remote '{remote_name}' has been deleted successfully!")

            # Refresh the remotes list
            self.load_remotes()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete remote: {str(e)}")
            
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

    def add_new_remote(self):
        """Open the new remote configuration dialog"""
        if not self.plugin_manager:
            messagebox.showerror("Error", "Plugin system not available. Please reinstall the application.")
            return

        # Get available plugins
        plugins = self.plugin_manager.get_available_plugins()
        if not plugins:
            messagebox.showinfo("No Plugins", "No remote plugins are available.")
            return

        # Create new window to select plugin type
        self.plugin_select_window = tk.Toplevel(self.root)
        self.plugin_select_window.title("Add New Remote")
        self.plugin_select_window.geometry("400x350")
        self.plugin_select_window.resizable(False, False)

        # Apply theme to plugin select window
        if self.current_theme == 'dark':
            self.plugin_select_window.configure(bg='#2d2d2d')
        else:
            self.plugin_select_window.configure(bg='#f0f0f0')

        # Center the plugin select window
        self.plugin_select_window.transient(self.root)
        # self.plugin_select_window.grab_set()  # Commented out to avoid conflicts

        # Add label
        label = ttk.Label(self.plugin_select_window, text="Select Remote Type", font=('Arial', 14, 'bold'))
        label.pack(pady=(20, 10))

        # Create a main frame to hold the plugin options
        main_frame = ttk.Frame(self.plugin_select_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create a frame with consistent background
        options_frame = tk.Frame(main_frame)
        if self.current_theme == 'dark':
            options_frame.configure(bg='#3d3d3d', relief='flat', bd=0)
        else:
            options_frame.configure(bg='#ffffff', relief='flat', bd=0)
        options_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas and scrollbar for scrolling the options
        canvas = tk.Canvas(options_frame)
        scrollbar = ttk.Scrollbar(options_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure canvas background to match theme
        if self.current_theme == 'dark':
            canvas.configure(bg='#3d3d3d', highlightthickness=0)
        else:
            canvas.configure(bg='#ffffff', highlightthickness=0)

        # Populate the scrollable frame with plugin options
        for plugin_name in plugins:
            plugin_info = self.plugin_manager.get_plugin_info(plugin_name)
            display_name = plugin_info.get('name', plugin_name)

            # Create simple button for each plugin without description
            plugin_btn = tk.Button(
                scrollable_frame,
                text=f"  {display_name}  ",
                command=lambda p=plugin_name: self._select_plugin(p),
                font=('Arial', 10, 'bold'),
                anchor='center',
                padx=10,
                pady=8,
                cursor='hand2',
                relief='flat',
                bd=1
            )

            # Apply theme to button with subtle styling
            if self.current_theme == 'dark':
                plugin_btn.configure(
                    bg='#4d4d4d',
                    fg='white',
                    activebackground='#5d5d5d',
                    activeforeground='white',
                    highlightbackground='#5d5d5d'
                )
            else:
                plugin_btn.configure(
                    bg='#e1e1e1',
                    fg='black',
                    activebackground='#d1d1d1',
                    activeforeground='black',
                    highlightbackground='#d1d1d1'
                )

            plugin_btn.pack(fill=tk.X, padx=5, pady=5, expand=True)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add buttons frame at the bottom
        button_frame = ttk.Frame(self.plugin_select_window)
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        # Help button on the left
        help_btn = ttk.Button(
            button_frame,
            text="Help",
            command=self._show_plugin_help
        )
        help_btn.pack(side=tk.LEFT)

        # Cancel and OK buttons on the right
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.plugin_select_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        ok_btn = ttk.Button(
            button_frame,
            text="OK",
            command=self._select_first_plugin  # Selects the first plugin by default
        )
        ok_btn.pack(side=tk.RIGHT)

    def _select_first_plugin(self):
        """Select the first plugin in the list if the user clicks OK"""
        plugins = self.plugin_manager.get_available_plugins()
        if plugins:
            self._select_plugin(plugins[0])

    def _select_plugin(self, plugin_name):
        """Handle plugin selection"""
        # Close the selection window
        self.plugin_select_window.destroy()

        # Get the plugin instance
        plugin = self.plugin_manager.get_plugin(plugin_name)

        # Open the configuration form for this plugin
        self.open_remote_config_form(plugin, plugin_name)

    def _show_plugin_help(self):
        """Show help information about plugins"""
        help_text = (
            "Plugin Help:\n\n"
            "Plugins allow you to add different types of remotes to Rclone.\n\n"
            "Each plugin provides a form with the necessary fields to configure\n"
            "that specific type of remote. After configuring, the remote will\n"
            "be saved to your rclone configuration file and will appear in\n"
            "the main list where you can mount, unmount, and manage it.\n\n"
            "To add a new remote:\n"
            "1. Select the type of remote you want to add\n"
            "2. Fill in the required configuration details\n"
            "3. Test the connection if possible\n"
            "4. Give the remote a name and save it"
        )
        messagebox.showinfo("Plugin Help", help_text)

    def _plugin_selected(self, event=None):
        """Handle plugin selection - kept for compatibility but not used with new UI"""
        # This method is not used with the new card-based UI, but kept for compatibility
        pass

    def open_remote_config_form(self, plugin, plugin_key):
        """Open the configuration form for a specific plugin"""
        # Create new window for remote configuration
        config_window = tk.Toplevel(self.root)
        config_window.title(f"Configure {plugin.get_name()}")
        config_window.geometry("500x600")
        config_window.resizable(True, True)

        # Apply theme to config window
        if self.current_theme == 'dark':
            config_window.configure(bg='#2d2d2d')
        else:
            config_window.configure(bg='#f0f0f0')

        # Center the config window
        config_window.transient(self.root)
        # config_window.grab_set()  # Commented out to avoid conflicts

        # Create a scrollable frame
        main_frame = ttk.Frame(config_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add description if available
        description = plugin.get_description()
        if description:
            desc_label = ttk.Label(scrollable_frame, text=description, wraplength=450)
            desc_label.pack(fill=tk.X, pady=(0, 10))

        # Add notes if available
        notes = plugin.get_notes()
        if notes:
            notes_frame = ttk.LabelFrame(scrollable_frame, text="Notes", padding=(10, 5))
            notes_frame.pack(fill=tk.X, pady=(0, 10))

            notes_label = ttk.Label(notes_frame, text=notes, wraplength=430)
            notes_label.pack(fill=tk.X)

        # Store configuration values
        config_vars = {}

        # Create the name field first
        name_field_frame = ttk.Frame(scrollable_frame)
        name_field_frame.pack(fill=tk.X, pady=5)

        name_label = ttk.Label(name_field_frame, text="Remote Name *:")
        name_label.pack(anchor=tk.W)

        name_var = tk.StringVar()
        config_vars['remote_name'] = name_var
        name_entry = ttk.Entry(name_field_frame, textvariable=name_var)
        name_entry.pack(fill=tk.X)

        name_desc_label = ttk.Label(name_field_frame, text="Enter a name for this remote (used to identify it in the list)", font=('Arial', 8))
        name_desc_label.pack(anchor=tk.W)

        # Get fields from plugin
        fields = plugin.get_fields()

        # Create UI elements for each field
        for field in fields:
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill=tk.X, pady=5)

            label = ttk.Label(field_frame, text=f"{field.label}{' *' if field.required else ''}:")
            label.pack(anchor=tk.W)

            if field.field_type == "bool":
                # Boolean field (checkbox)
                var = tk.BooleanVar(value=field.default.lower() in ['true', '1', 'yes'] if field.default else False)
                config_vars[field.name] = var
                checkbox = ttk.Checkbutton(field_frame, variable=var, text="")
                checkbox.pack(fill=tk.X)
            elif field.field_type == "choice":
                # Choice field (combobox)
                var = tk.StringVar(value=field.default)
                config_vars[field.name] = var
                combobox = ttk.Combobox(field_frame, textvariable=var, values=field.choices, state="readonly")
                combobox.pack(fill=tk.X)
                if field.default:
                    combobox.set(field.default)
            elif field.field_type == "file":
                # File field with browse button
                var = tk.StringVar(value=field.default)
                config_vars[field.name] = var

                file_frame = ttk.Frame(field_frame)
                file_frame.pack(fill=tk.X, pady=2)

                entry = ttk.Entry(file_frame, textvariable=var)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                browse_btn = ttk.Button(file_frame, text="Browse", command=lambda v=var, f=field: self._browse_file(v, f))
                browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
            elif field.field_type == "password":
                # Password field
                var = tk.StringVar(value=field.default)
                config_vars[field.name] = var
                entry = ttk.Entry(field_frame, textvariable=var, show="*")
                entry.pack(fill=tk.X)
            elif field.field_type in ["int", "float"]:
                # Number field
                var = tk.StringVar(value=field.default)
                config_vars[field.name] = var
                entry = ttk.Entry(field_frame, textvariable=var)
                entry.pack(fill=tk.X)
            else:
                # Text field
                var = tk.StringVar(value=field.default)
                config_vars[field.name] = var
                entry = ttk.Entry(field_frame, textvariable=var)
                entry.pack(fill=tk.X)

            # Add description if available
            if field.description:
                desc_label = ttk.Label(field_frame, text=field.description, font=('Arial', 8))
                desc_label.pack(anchor=tk.W)

        # Add advanced fields if available
        advanced_fields = plugin.get_advanced_fields()
        if advanced_fields:
            advanced_frame = ttk.LabelFrame(scrollable_frame, text="Advanced Options", padding=(10, 5))
            advanced_frame.pack(fill=tk.X, pady=(10, 0))

            for field in advanced_fields:
                field_frame = ttk.Frame(advanced_frame)
                field_frame.pack(fill=tk.X, pady=5)

                label = ttk.Label(field_frame, text=f"{field.label}{' *' if field.required else ''}:")
                label.pack(anchor=tk.W)

                if field.field_type == "bool":
                    var = tk.BooleanVar(value=field.default.lower() in ['true', '1', 'yes'] if field.default else False)
                    config_vars[field.name] = var
                    checkbox = ttk.Checkbutton(field_frame, variable=var, text="")
                    checkbox.pack(fill=tk.X)
                elif field.field_type == "choice":
                    var = tk.StringVar(value=field.default)
                    config_vars[field.name] = var
                    combobox = ttk.Combobox(field_frame, textvariable=var, values=field.choices, state="readonly")
                    combobox.pack(fill=tk.X)
                    if field.default:
                        combobox.set(field.default)
                elif field.field_type == "file":
                    var = tk.StringVar(value=field.default)
                    config_vars[field.name] = var

                    file_frame = ttk.Frame(field_frame)
                    file_frame.pack(fill=tk.X, pady=2)

                    entry = ttk.Entry(file_frame, textvariable=var)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

                    browse_btn = ttk.Button(file_frame, text="Browse", command=lambda v=var, f=field: self._browse_file(v, f))
                    browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
                elif field.field_type == "password":
                    var = tk.StringVar(value=field.default)
                    config_vars[field.name] = var
                    entry = ttk.Entry(field_frame, textvariable=var, show="*")
                    entry.pack(fill=tk.X)
                elif field.field_type in ["int", "float"]:
                    var = tk.StringVar(value=field.default)
                    config_vars[field.name] = var
                    entry = ttk.Entry(field_frame, textvariable=var)
                    entry.pack(fill=tk.X)
                else:
                    var = tk.StringVar(value=field.default)
                    config_vars[field.name] = var
                    entry = ttk.Entry(field_frame, textvariable=var)
                    entry.pack(fill=tk.X)

                # Add description if available
                if field.description:
                    desc_label = ttk.Label(field_frame, text=field.description, font=('Arial', 8))
                    desc_label.pack(anchor=tk.W)

        # Add buttons frame
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        def test_connection():
            # Collect configuration values
            config_data = {}
            for name, var in config_vars.items():
                if name != 'remote_name':  # Skip the remote name field
                    value = var.get()
                    if isinstance(value, bool):
                        config_data[name] = str(value).lower()
                    else:
                        config_data[name] = str(value) if value else ""

            # Validate configuration
            validation = plugin.validate_config(config_data)
            if not validation.success:
                messagebox.showerror("Validation Error", validation.message)
                return

            # Test connection
            test_result = plugin.test_connection(config_data)
            if test_result.success:
                messagebox.showinfo("Test Successful", test_result.message)
            else:
                messagebox.showerror("Test Failed", test_result.message)

        def save_remote():
            # Collect configuration values
            config_data = {}
            for name, var in config_vars.items():
                if name != 'remote_name':  # Skip the remote name field
                    value = var.get()
                    if isinstance(value, bool):
                        config_data[name] = str(value).lower()
                    else:
                        config_data[name] = str(value) if value else ""

            # Validate configuration
            validation = plugin.validate_config(config_data)
            if not validation.success:
                messagebox.showerror("Validation Error", validation.message)
                return

            # Get the remote name
            remote_name = config_vars['remote_name'].get()
            if not remote_name:
                messagebox.showerror("Error", "Remote name is required")
                return

            # Ask for confirmation if the connection test hasn't been performed
            if remote_name:  # If a name exists, ask about saving
                # Check if user wants to save even with errors
                test_result = plugin.test_connection(config_data)
                if not test_result.success:
                    response = messagebox.askyesno(
                        "Configuration Not Working",
                        f"Connection test failed: {test_result.message}\n\n"
                        f"Do you still want to save this configuration?",
                        icon='warning'
                    )
                    if not response:
                        return

            # Save to rclone config
            self.save_remote_config(remote_name, plugin, config_data, config_window)

        # Add test, save and cancel buttons
        test_btn = ttk.Button(button_frame, text="Test Connection", command=test_connection)
        test_btn.pack(side=tk.RIGHT, padx=(5, 0))

        save_btn = ttk.Button(button_frame, text="Save", command=save_remote)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=config_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)

        # Add scrollbar to canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _browse_file(self, var, field):
        """Open file dialog to browse for a file"""
        file_path = filedialog.askopenfilename(
            title=f"Select {field.label}",
            initialdir=os.path.expanduser('~'),
            filetypes=[(field.label, field.file_filter), ("All files", "*.*")]
        )
        if file_path:
            var.set(file_path)

    def save_remote_config(self, remote_name, plugin, config_data, window):
        """Save the remote configuration to rclone.conf"""
        try:
            # Get the config format from plugin
            config_format = plugin.get_config_format(config_data)

            # Read the existing config file
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = configparser.ConfigParser()
                    config.read(self.config_path)
            else:
                # Create a new config if it doesn't exist
                config = configparser.ConfigParser()

            # Add the new remote
            if remote_name in config:
                # Ask user if they want to overwrite
                result = messagebox.askyesno(
                    "Remote Exists",
                    f"Remote '{remote_name}' already exists. Do you want to overwrite it?",
                    icon='warning'
                )
                if not result:
                    return
                config.remove_section(remote_name)

            # Create the section with the remote type as the 'type' field
            config.add_section(remote_name)
            for key, value in config_format.items():
                # For the config format, we need to make sure type is set correctly
                config.set(remote_name, key, str(value))

            # Write the config back to the file
            with open(self.config_path, 'w') as f:
                config.write(f)

            # Show success message
            messagebox.showinfo("Success", f"Remote '{remote_name}' has been saved successfully!")

            # Close the configuration window
            window.destroy()

            # Refresh the remotes list
            self.load_remotes()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save remote: {str(e)}")


def main():
    root = tk.Tk()
    app = RcloneManager(root)
    # Apply initial theme
    app.apply_theme()
    root.mainloop()


if __name__ == "__main__":
    main()