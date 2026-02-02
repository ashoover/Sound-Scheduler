#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import json
from playsound import playsound

class SoundPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sound Player Scheduler")
        self.root.geometry("600x400")
        
        # Set custom icon if available
        try:
            if os.path.exists("app.ico"):
                self.root.iconbitmap("app.ico")
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # List to store sound tasks
        self.sound_tasks = []
        self.running_tasks = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Add Sound button
        self.add_sound_btn = ttk.Button(main_frame, text="Add Sound", command=self.add_sound_dialog)
        self.add_sound_btn.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        # Sound list with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.sound_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sound_listbox.yview)
        self.sound_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.sound_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.sound_listbox.bind('<Double-Button-1>', self.edit_sound_task)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=2, column=0, pady=(10, 0))
        
    def add_sound_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Sound Task")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # File selection
        file_frame = ttk.Frame(dialog, padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        ttk.Label(file_frame, text="Sound File:").grid(row=0, column=0, sticky="w")
        
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=40)
        file_entry.grid(row=0, column=1, padx=(10, 10), sticky="ew")
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_sound_file)
        browse_btn.grid(row=0, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Interval input
        interval_frame = ttk.Frame(dialog, padding="10")
        interval_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Label(interval_frame, text="Play every (minutes):").grid(row=0, column=0, sticky="w")
        
        self.interval_var = tk.StringVar(value="5")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=0, column=1, padx=(10, 0), sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.grid(row=2, column=0, columnspan=2)
        
        ttk.Button(button_frame, text="Add", command=lambda: self.add_sound(dialog)).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(row=0, column=1)
        
        # Store dialog reference for browse function
        self.current_dialog = dialog
        
    def browse_sound_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=[
                ("Audio Files", "*.wav *.mp3"),
                ("WAV Files", "*.wav"),
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.file_var.set(file_path)
            
    def add_sound(self, dialog):
        file_path = self.file_var.get().strip()
        interval_str = self.interval_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a sound file")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Sound file does not exist")
            return
            
        try:
            interval = float(interval_str)
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for minutes")
            return
            

        
        # Add sound task
        task = {
            'file': file_path,
            'interval': interval,
            'name': os.path.basename(file_path),
            'last_played': 0,
            'active': True
        }
        
        self.sound_tasks.append(task)
        
        # Add to listbox
        display_text = f"{task['name']} - Every {task['interval']} minutes"
        self.sound_listbox.insert(tk.END, display_text)
        
        # Start the background thread for this task
        self.start_sound_task(task)
        
        self.status_label.config(text=f"Added: {task['name']}")
        dialog.destroy()
        
    def edit_sound_task(self, event=None):
        selection = self.sound_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        task = self.sound_tasks[index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Sound Task")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Current file display
        file_frame = ttk.Frame(dialog, padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        ttk.Label(file_frame, text="Sound File:").grid(row=0, column=0, sticky="w")
        ttk.Label(file_frame, text=task['file'], wraplength=300).grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        file_frame.columnconfigure(1, weight=1)
        
        # Interval input
        interval_frame = ttk.Frame(dialog, padding="10")
        interval_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Label(interval_frame, text="Play every (minutes):").grid(row=0, column=0, sticky="w")
        
        interval_var = tk.StringVar(value=str(task['interval']))
        interval_entry = ttk.Entry(interval_frame, textvariable=interval_var, width=10)
        interval_entry.grid(row=0, column=1, padx=(10, 0), sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.grid(row=2, column=0, columnspan=2)
        
        def save_changes():
            try:
                new_interval = float(interval_var.get())
                if new_interval <= 0:
                    raise ValueError("Interval must be positive")
                    
                task['interval'] = new_interval
                task['active'] = True
                
                # Update listbox display
                display_text = f"{task['name']} - Every {task['interval']} minutes"
                self.sound_listbox.delete(index)
                self.sound_listbox.insert(index, display_text)
                self.sound_listbox.selection_set(index)
                
                self.status_label.config(text=f"Updated: {task['name']}")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number for minutes")
                
        def delete_task():
            if messagebox.askyesno("Confirm Delete", f"Delete sound task '{task['name']}'?"):
                task['active'] = False
                self.sound_tasks.pop(index)
                self.sound_listbox.delete(index)
                self.status_label.config(text=f"Deleted: {task['name']}")
                dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_changes).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=delete_task).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(row=0, column=2)
        
    def start_sound_task(self, task):
        def play_loop():
            while task['active']:
                current_time = time.time()
                
                if current_time - task['last_played'] >= task['interval'] * 60:
                    try:
                        self.play_sound(task['file'])
                        task['last_played'] = current_time
                    except Exception as e:
                        print(f"Error playing {task['file']}: {e}")
                        
                time.sleep(1)  # Check every second
                
        thread = threading.Thread(target=play_loop, daemon=True)
        thread.start()
        self.running_tasks.append(thread)
        
    def play_sound(self, file_path):
        """Play sound file using playsound module"""
        try:
            # playsound supports both WAV and MP3 files
            playsound(file_path, block=False)
        except Exception as e:
            print(f"Error playing {file_path}: {e}")
            # Fallback to system default player
            try:
                os.startfile(file_path)
            except:
                print(f"Could not play {file_path} with system player either")
        
    def on_closing(self):
        # Stop all active tasks
        for task in self.sound_tasks:
            task['active'] = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundPlayerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()