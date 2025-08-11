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
from pathlib import Path

class RcloneManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Rclone GUI Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
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
        else:
            # Light theme colors
            self.style.configure('TFrame', background='#f0f0f0')
            self.style.configure('TLabel', background='#f0f0f0', foreground='black')
            self.style.configure('Header.TLabel', background='#f0f0f0', foreground='black', font=('Arial', 14, 'bold'))
            self.style.configure('Status.TLabel', background='#f0f0f0', foreground='black', font=('Arial', 10))
            
            # Button styling
            self.style.configure('TButton', background='#e1e1e1', foreground='black')
            
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
            
        # Update theme button text
        self.theme_btn.configure(text="☀️ Light Mode" if self.current_theme == 'dark' else "🌙 Dark Mode")
        
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
            if len(values) > 2 and values[2] == "Yes":  # If mounted
                self.tree.item(item_id, tags=('mounted',))
            else:
                self.tree.item(item_id, tags=())
            
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_label = ttk.Label(self.main_frame, text="Rclone Remote Manager", style='Header.TLabel')
        self.header_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Ready", style='Status.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview for remotes
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ('Remote', 'Type', 'Mounted', 'Mount Point')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')
        
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
        
        self.theme_btn = ttk.Button(self.button_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
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
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
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
            
    def show_progress(self, show=True):
        if show:
            self.progress.start(10)
        else:
            self.progress.stop()
            
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
        self.show_status("Loading remotes...")
        
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
            
        config_path = os.path.expanduser('~/.config/rclone/rclone.conf')
        
        if not os.path.exists(config_path):
            self.show_status("No rclone config found", 'error')
            self.show_progress(False)
            return
            
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
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
            remotes.append((section, remote_type, mounted_text, mount_point))
            
        # Sort remotes by name
        remotes.sort(key=lambda x: x[0].lower())
        
        # Add to treeview
        for remote in remotes:
            # Apply 'mounted' tag if remote is mounted
            is_mounted = remote[2] == "Yes"  # Check the "Mounted" column
            tags = ('mounted',) if is_mounted else ()
            item_id = self.tree.insert('', tk.END, values=remote, tags=tags)
            # If this is the previously selected remote, store its new item ID
            if selected_remote_name and remote[0] == selected_remote_name:
                self.selected_item = item_id
                
        self.show_status(f"Loaded {len(remotes)} remotes", 'success')
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
            is_mounted = values[2] == "Yes"
            
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
        
        if len(values) > 3:
            mount_point = values[3]
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
            result = subprocess.run(['rclone', 'lsf', f'{remote_name}:'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return True, "Connection successful"
            else:
                return False, f"Connection failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Connection test timed out"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
            
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
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.PIPE)
            
            # Give it a moment to see if it fails immediately
            try:
                process.wait(timeout=2)
                # If we get here, it failed to start
                stderr = process.stderr.read().decode() if process.stderr else ""
                return False, f"Mount failed: {stderr}"
            except subprocess.TimeoutExpired:
                # This is good - it means the mount is still running
                pass
                
            return True, f"Successfully mounted {remote_name} at {mount_point}"
            
        except Exception as e:
            return False, f"Mount failed: {str(e)}"
            
    def unmount_remote(self, remote_name):
        """Unmount remote"""
        try:
            mount_point = str(self.get_mount_dir(remote_name))
            
            # Check if mounted
            if not self.is_mounted(mount_point):
                return True, f"{remote_name} is not mounted"
                
            # Try fusermount first (Linux)
            try:
                result = subprocess.run(['fusermount', '-u', mount_point], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True, f"Successfully unmounted {remote_name}"
                else:
                    # Try umount as fallback
                    result = subprocess.run(['umount', mount_point], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True, f"Successfully unmounted {remote_name}"
                    else:
                        return False, f"Unmount failed: {result.stderr}"
            except FileNotFoundError:
                # Try umount directly
                result = subprocess.run(['umount', mount_point], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True, f"Successfully unmounted {remote_name}"
                else:
                    return False, f"Unmount failed: {result.stderr}"
                    
        except Exception as e:
            return False, f"Unmount failed: {str(e)}"
            
    def test_selected(self):
        """Test connection to selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            messagebox.showwarning("Warning", "Please select a remote to test")
            return
            
        self.show_progress(True)
        self.show_status(f"Testing connection to {remote_name}...")
        
        success, message = self.test_connection(remote_name)
        
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
            
        self.show_progress(True)
        self.show_status(f"Mounting {remote_name}...")
        
        # Test connection first
        success, message = self.test_connection(remote_name)
        if not success:
            self.show_progress(False)
            self.show_status(message, 'error')
            messagebox.showerror("Mount Failed", 
                               f"Cannot mount {remote_name} - connection test failed:\n{message}")
            return
            
        # Proceed with mount
        success, message = self.mount_remote(remote_name)
        
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
            
        self.show_progress(True)
        self.show_status(f"Unmounting {remote_name}...")
        
        success, message = self.unmount_remote(remote_name)
        
        self.show_progress(False)
        if success:
            self.show_status(message, 'success')
            messagebox.showinfo("Unmount Successful", message)
            self.refresh_remotes()
        else:
            self.show_status(message, 'error')
            messagebox.showerror("Unmount Failed", message)
            
    def toggle_cron(self):
        """Toggle cron entry for selected remote"""
        remote_name = self.get_selected_remote()
        if not remote_name:
            self.cron_var.set(False)
            messagebox.showwarning("Warning", "Please select a remote first")
            return
            
        if self.cron_var.get():
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
            else:
                self.show_status(f"Failed to remove from crontab: {stderr.decode()}", 'error')
                
        except Exception as e:
            self.show_status(f"Cron operation failed: {str(e)}", 'error')


def main():
    root = tk.Tk()
    app = RcloneManager(root)
    # Apply initial theme
    app.apply_theme()
    root.mainloop()


if __name__ == "__main__":
    main()