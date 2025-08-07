import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
import threading
import time
from pathlib import Path
import json
import mutagen
from mutagen.mp3 import MP3
from PIL import Image, ImageTk
import io

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern MP3 Player")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Player state
        self.current_track = None
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        
        # Load settings
        self.settings_file = "player_settings.json"
        self.load_settings()
        
        self.setup_ui()
        self.setup_bindings()
        
    def create_default_artwork(self):
        """Create a default music note icon"""
        # Create a simple music note icon using PIL
        size = 120
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Create a simple music note shape (simplified)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw a simple music note
        # Note head
        draw.ellipse([size//2-15, size//2-10, size//2+15, size//2+10], fill='#ffffff')
        # Note stem
        draw.rectangle([size//2+10, size//2-30, size//2+15, size//2+10], fill='#ffffff')
        # Flag
        draw.ellipse([size//2+15, size//2-30, size//2+35, size//2-10], fill='#ffffff')
        
        return ImageTk.PhotoImage(img)
    
    def extract_artwork(self, file_path):
        """Extract artwork from MP3 file"""
        try:
            audio = MP3(file_path)
            if audio.tags:
                # Look for artwork in ID3 tags
                for key in ['APIC:', 'APIC:0', 'APIC:1', 'APIC:2', 'APIC:3']:
                    if key in audio.tags:
                        artwork_data = audio.tags[key].data
                        img = Image.open(io.BytesIO(artwork_data))
                        return img
                
                # Try other common artwork keys
                for key in audio.tags.keys():
                    if 'APIC' in str(key):
                        artwork_data = audio.tags[key].data
                        img = Image.open(io.BytesIO(artwork_data))
                        return img
                        
        except Exception as e:
            self.status_var.set(f"Artwork extraction failed: {str(e)}")
        
        return None
    
    def display_artwork(self, file_path):
        """Display artwork for the given file"""
        try:
            artwork = self.extract_artwork(file_path)
            
            if artwork:
                # Resize artwork to fit display
                size = 120
                artwork = artwork.resize((size, size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(artwork)
                
                # Update the artwork label
                self.artwork_label.configure(image=photo)
                self.artwork_label.image = photo  # Keep a reference
                
                self.status_var.set("Artwork loaded successfully")
            else:
                # Use default artwork
                self.artwork_label.configure(image=self.default_artwork)
                self.artwork_label.image = self.default_artwork
                
        except Exception as e:
            # Use default artwork on error
            self.artwork_label.configure(image=self.default_artwork)
            self.artwork_label.image = self.default_artwork
            self.status_var.set(f"Artwork display failed: {str(e)}")
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🎵 Modern MP3 Player", 
                              font=('Arial', 24, 'bold'), 
                              fg='#ffffff', bg='#2b2b2b')
        title_label.pack(pady=(0, 20))
        
        # Current track display with artwork
        self.track_frame = tk.Frame(main_frame, bg='#3b3b3b', relief=tk.RAISED, bd=2)
        self.track_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Track info and artwork container
        self.track_info_frame = tk.Frame(self.track_frame, bg='#3b3b3b')
        self.track_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Artwork display
        self.artwork_frame = tk.Frame(self.track_info_frame, bg='#3b3b3b')
        self.artwork_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # Default artwork (music note icon)
        self.default_artwork = self.create_default_artwork()
        self.artwork_label = tk.Label(self.artwork_frame, image=self.default_artwork, 
                                     bg='#3b3b3b', relief=tk.RAISED, bd=1)
        self.artwork_label.pack()
        
        # Track info container
        self.track_info_container = tk.Frame(self.track_info_frame, bg='#3b3b3b')
        self.track_info_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.track_label = tk.Label(self.track_info_container, text="No track selected", 
                                   font=('Arial', 12), 
                                   fg='#ffffff', bg='#3b3b3b', wraplength=500)
        self.track_label.pack(pady=(0, 5))
        
        # Metadata display
        self.metadata_frame = tk.Frame(self.track_frame, bg='#3b3b3b')
        self.metadata_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Metadata labels
        self.metadata_labels = {}
        metadata_fields = [
            ('artist', 'Artist:'),
            ('title', 'Title:'),
            ('album', 'Album:'),
            ('year', 'Year:'),
            ('genre', 'Genre:'),
            ('duration', 'Duration:'),
            ('bitrate', 'Bitrate:'),
            ('filesize', 'File Size:')
        ]
        
        for i, (key, label_text) in enumerate(metadata_fields):
            row = i // 2
            col = i % 2
            
            label_frame = tk.Frame(self.metadata_frame, bg='#3b3b3b')
            label_frame.grid(row=row, column=col, sticky='ew', padx=5, pady=2)
            
            tk.Label(label_frame, text=label_text, 
                    font=('Arial', 9, 'bold'), 
                    fg='#cccccc', bg='#3b3b3b').pack(side=tk.LEFT)
            
            self.metadata_labels[key] = tk.Label(label_frame, text="N/A", 
                                               font=('Arial', 9), 
                                               fg='#ffffff', bg='#3b3b3b')
            self.metadata_labels[key].pack(side=tk.LEFT, padx=(5, 0))
        
        # Configure grid weights
        self.metadata_frame.grid_columnconfigure(0, weight=1)
        self.metadata_frame.grid_columnconfigure(1, weight=1)
        
        # Progress bar
        self.progress_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                           variable=self.progress_var,
                                           maximum=100, length=700)
        self.progress_bar.pack()
        
        # Time labels
        self.time_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.time_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.current_time_label = tk.Label(self.time_frame, text="00:00", 
                                         font=('Arial', 10), 
                                         fg='#cccccc', bg='#2b2b2b')
        self.current_time_label.pack(side=tk.LEFT)
        
        self.total_time_label = tk.Label(self.time_frame, text="00:00", 
                                       font=('Arial', 10), 
                                       fg='#cccccc', bg='#2b2b2b')
        self.total_time_label.pack(side=tk.RIGHT)
        
        # Control buttons
        self.control_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.control_frame.pack(pady=20)
        
        # Previous button
        self.prev_button = tk.Button(self.control_frame, text="⏮", 
                                    font=('Arial', 16), 
                                    command=self.previous_track,
                                    bg='#4a4a4a', fg='#ffffff',
                                    relief=tk.FLAT, padx=10, pady=5)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        # Play/Pause button
        self.play_button = tk.Button(self.control_frame, text="▶", 
                                    font=('Arial', 18), 
                                    command=self.play_pause,
                                    bg='#4a4a4a', fg='#ffffff',
                                    relief=tk.FLAT, padx=15, pady=5)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_button = tk.Button(self.control_frame, text="⏹", 
                                    font=('Arial', 16), 
                                    command=self.stop,
                                    bg='#4a4a4a', fg='#ffffff',
                                    relief=tk.FLAT, padx=10, pady=5)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Next button
        self.next_button = tk.Button(self.control_frame, text="⏭", 
                                    font=('Arial', 16), 
                                    command=self.next_track,
                                    bg='#4a4a4a', fg='#ffffff',
                                    relief=tk.FLAT, padx=10, pady=5)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Volume control
        self.volume_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.volume_frame.pack(pady=10)
        
        tk.Label(self.volume_frame, text="🔊", font=('Arial', 12), 
                fg='#ffffff', bg='#2b2b2b').pack(side=tk.LEFT, padx=(0, 5))
        
        self.volume_var = tk.DoubleVar(value=70)
        self.volume_scale = ttk.Scale(self.volume_frame, from_=0, to=100,
                                     variable=self.volume_var, orient=tk.HORIZONTAL,
                                     length=200, command=self.set_volume)
        self.volume_scale.pack(side=tk.LEFT, padx=5)
        
        self.volume_label = tk.Label(self.volume_frame, text="70%", 
                                   font=('Arial', 10), 
                                   fg='#cccccc', bg='#2b2b2b')
        self.volume_label.pack(side=tk.LEFT, padx=5)
        
        # File operations
        self.file_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.file_frame.pack(pady=20)
        
        self.open_button = tk.Button(self.file_frame, text="📁 Open File", 
                                    command=self.open_file,
                                    bg='#4a4a4a', fg='#ffffff',
                                    relief=tk.FLAT, padx=15, pady=5)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.open_folder_button = tk.Button(self.file_frame, text="📂 Open Folder", 
                                          command=self.open_folder,
                                          bg='#4a4a4a', fg='#ffffff',
                                          relief=tk.FLAT, padx=15, pady=5)
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(self.file_frame, text="🗑 Clear Playlist", 
                                    command=self.clear_playlist,
                                    bg='#4a4a4a', fg='#ffffff',
                                    relief=tk.FLAT, padx=15, pady=5)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Playlist
        self.playlist_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        tk.Label(self.playlist_frame, text="Playlist:", 
                font=('Arial', 12, 'bold'), 
                fg='#ffffff', bg='#2b2b2b').pack(anchor=tk.W)
        
        # Playlist listbox with scrollbar
        listbox_frame = tk.Frame(self.playlist_frame, bg='#2b2b2b')
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.playlist_listbox = tk.Listbox(listbox_frame, 
                                          bg='#3b3b3b', fg='#ffffff',
                                          selectbackground='#4a4a4a',
                                          font=('Arial', 10),
                                          height=8)
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.playlist_listbox.yview)
        
        # Bind double-click to play selected track
        self.playlist_listbox.bind('<Double-Button-1>', self.play_selected_track)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var,
                                 relief=tk.SUNKEN, anchor=tk.W,
                                 bg='#1a1a1a', fg='#cccccc')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_bindings(self):
        # Bind progress bar click
        self.progress_bar.bind('<Button-1>', self.seek)
        
        # Bind keyboard shortcuts
        self.root.bind('<space>', lambda e: self.play_pause())
        self.root.bind('<Left>', lambda e: self.previous_track())
        self.root.bind('<Right>', lambda e: self.next_track())
        self.root.bind('<Up>', lambda e: self.volume_up())
        self.root.bind('<Down>', lambda e: self.volume_down())
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.volume_var.set(settings.get('volume', 70))
        except:
            pass
            
    def save_settings(self):
        try:
            settings = {
                'volume': self.volume_var.get()
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except:
            pass
            
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if file_path:
            self.add_to_playlist(file_path)
            
    def open_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with MP3 Files")
        if folder_path:
            self.add_folder_to_playlist(folder_path)
            
    def get_metadata(self, file_path):
        """Extract metadata from MP3 file"""
        metadata = {
            'artist': 'Unknown',
            'title': 'Unknown',
            'album': 'Unknown',
            'year': 'Unknown',
            'genre': 'Unknown',
            'duration': 'Unknown',
            'bitrate': 'Unknown',
            'filesize': 'Unknown'
        }
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                metadata['filesize'] = f"{file_size} B"
            elif file_size < 1024 * 1024:
                metadata['filesize'] = f"{file_size / 1024:.1f} KB"
            else:
                metadata['filesize'] = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Get MP3 metadata
            audio = MP3(file_path)
            
            # Duration
            if audio.info.length:
                minutes = int(audio.info.length // 60)
                seconds = int(audio.info.length % 60)
                metadata['duration'] = f"{minutes:02d}:{seconds:02d}"
            
            # Bitrate
            if audio.info.bitrate:
                if audio.info.bitrate < 1000:
                    metadata['bitrate'] = f"{audio.info.bitrate} bps"
                else:
                    metadata['bitrate'] = f"{audio.info.bitrate / 1000:.0f} kbps"
            
            # ID3 tags
            if audio.tags:
                # Artist
                if 'TPE1' in audio.tags:
                    metadata['artist'] = str(audio.tags['TPE1'])
                elif 'artist' in audio.tags:
                    metadata['artist'] = str(audio.tags['artist'])
                
                # Title
                if 'TIT2' in audio.tags:
                    metadata['title'] = str(audio.tags['TIT2'])
                elif 'title' in audio.tags:
                    metadata['title'] = str(audio.tags['title'])
                
                # Album
                if 'TALB' in audio.tags:
                    metadata['album'] = str(audio.tags['TALB'])
                elif 'album' in audio.tags:
                    metadata['album'] = str(audio.tags['album'])
                
                # Year
                if 'TDRC' in audio.tags:
                    year_str = str(audio.tags['TDRC'])
                    if year_str.isdigit():
                        metadata['year'] = year_str
                elif 'year' in audio.tags:
                    metadata['year'] = str(audio.tags['year'])
                
                # Genre
                if 'TCON' in audio.tags:
                    metadata['genre'] = str(audio.tags['TCON'])
                elif 'genre' in audio.tags:
                    metadata['genre'] = str(audio.tags['genre'])
            
            # If no title found, use filename
            if metadata['title'] == 'Unknown':
                metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
                
        except Exception as e:
            # If metadata extraction fails, use filename as title
            metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
            self.status_var.set(f"Metadata extraction failed: {str(e)}")
        
        return metadata
    
    def display_metadata(self, file_path):
        """Display metadata for the given file"""
        metadata = self.get_metadata(file_path)
        
        for key, label in self.metadata_labels.items():
            if key in metadata:
                label.config(text=metadata[key])
            else:
                label.config(text="N/A")
    
    def add_to_playlist(self, file_path):
        if file_path not in self.playlist:
            self.playlist.append(file_path)
            filename = os.path.basename(file_path)
            self.playlist_listbox.insert(tk.END, filename)
            self.status_var.set(f"Added: {filename}")
            
    def add_folder_to_playlist(self, folder_path):
        mp3_files = []
        for ext in ['*.mp3', '*.MP3']:
            # Use rglob to search recursively through all subfolders
            mp3_files.extend(Path(folder_path).rglob(ext))
        
        if mp3_files:
            for file_path in sorted(mp3_files):
                self.add_to_playlist(str(file_path))
            self.status_var.set(f"Added {len(mp3_files)} files from folder and subfolders")
        else:
            messagebox.showwarning("No MP3 files found", 
                                 "No MP3 files were found in the selected folder or its subfolders.")
            
    def clear_playlist(self):
        self.stop()
        self.playlist.clear()
        self.playlist_listbox.delete(0, tk.END)
        self.current_track = None
        self.current_index = 0
        self.track_label.config(text="No track selected")
        
        # Clear metadata display
        for label in self.metadata_labels.values():
            label.config(text="N/A")
        
        # Reset artwork to default
        self.artwork_label.configure(image=self.default_artwork)
        self.artwork_label.image = self.default_artwork
        
        self.status_var.set("Playlist cleared")
        
    def play_selected_track(self, event=None):
        selection = self.playlist_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.play_current_track()
            
    def play_current_track(self):
        if 0 <= self.current_index < len(self.playlist):
            self.current_track = self.playlist[self.current_index]
            self.playlist_listbox.selection_clear(0, tk.END)
            self.playlist_listbox.selection_set(self.current_index)
            self.playlist_listbox.see(self.current_index)
            
            try:
                pygame.mixer.music.load(self.current_track)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.play_button.config(text="⏸")
                
                # Display metadata and artwork
                self.display_metadata(self.current_track)
                self.display_artwork(self.current_track)
                
                # Get metadata for display name
                metadata = self.get_metadata(self.current_track)
                display_name = metadata.get('title', os.path.basename(self.current_track))
                artist = metadata.get('artist', 'Unknown Artist')
                
                self.track_label.config(text=f"Now playing: {artist} - {display_name}")
                self.status_var.set(f"Playing: {display_name}")
                
                # Start progress update thread
                self.progress_thread = threading.Thread(target=self.update_progress, daemon=True)
                self.progress_thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not play file: {str(e)}")
                self.status_var.set("Error playing file")
                
    def play_pause(self):
        if not self.current_track:
            if self.playlist:
                self.play_current_track()
            return
            
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_button.config(text="▶")
            self.status_var.set("Paused")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_button.config(text="⏸")
            self.status_var.set("Playing")
        else:
            self.play_current_track()
            
    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.play_button.config(text="▶")
        self.progress_var.set(0)
        self.current_time_label.config(text="00:00")
        self.status_var.set("Stopped")
        
    def next_track(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_current_track()
            
    def previous_track(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play_current_track()
            
    def set_volume(self, value):
        volume = float(value) / 100.0
        pygame.mixer.music.set_volume(volume)
        self.volume_label.config(text=f"{int(value)}%")
        self.save_settings()
        
    def volume_up(self):
        current_volume = self.volume_var.get()
        new_volume = min(100, current_volume + 10)
        self.volume_var.set(new_volume)
        self.set_volume(new_volume)
        
    def volume_down(self):
        current_volume = self.volume_var.get()
        new_volume = max(0, current_volume - 10)
        self.volume_var.set(new_volume)
        self.set_volume(new_volume)
        
    def seek(self, event):
        if self.current_track and self.is_playing:
            # Get click position on progress bar
            x = event.x
            width = self.progress_bar.winfo_width()
            percentage = x / width
            
            # Get total duration and seek
            try:
                # This is a simplified seek - pygame doesn't have direct seek support
                # In a real implementation, you'd need to use a different library
                self.status_var.set("Seek not supported in this version")
            except:
                pass
                
    def update_progress(self):
        while self.is_playing and not self.is_paused:
            try:
                # Get current position and duration
                current_pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
                
                # Update progress bar (simplified - assumes 3 minute songs)
                # In a real implementation, you'd get actual duration
                total_duration = 180  # 3 minutes as default
                progress = (current_pos / total_duration) * 100
                self.progress_var.set(min(progress, 100))
                
                # Update time labels
                current_min = int(current_pos // 60)
                current_sec = int(current_pos % 60)
                self.current_time_label.config(text=f"{current_min:02d}:{current_sec:02d}")
                
                # Check if song ended
                if not pygame.mixer.music.get_busy() and self.is_playing:
                    self.root.after(0, self.next_track)
                    break
                    
                time.sleep(0.1)
                
            except:
                break
                
    def on_closing(self):
        self.save_settings()
        pygame.mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MP3Player(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
