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
import requests
import urllib.request
import tempfile

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 GitHub Music Streamer")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Player state
        self.current_track = None
        self.playlist = []
        self.original_playlist = []  # Store original order for shuffle toggle
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.is_shuffled = False
        
        # Load settings
        self.settings_file = "player_settings.json"
        self.load_settings()
        
        self.setup_ui()
        self.setup_bindings()
        
        # Auto-fetch songs on startup
        self.root.after(1000, self.auto_fetch_songs)
        
    def auto_fetch_songs(self):
        """Automatically fetch songs from GitHub on startup"""
        self.status_var.set("🌐 Auto-loading songs from GitHub...")
        self.root.update()
        
        # Start fetching in a separate thread to avoid blocking UI
        fetch_thread = threading.Thread(target=self.stream_from_github, daemon=True)
        fetch_thread.start()
        
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
    

        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🌐 GitHub Music Streamer", 
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
        
        # Shuffle button
        self.shuffle_button = tk.Button(self.control_frame, text="🔀", 
                                      font=('Arial', 16), 
                                      command=self.toggle_shuffle,
                                      bg='#4a4a4a', fg='#ffffff',
                                      relief=tk.FLAT, padx=10, pady=5)
        self.shuffle_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # Streaming operations
        self.stream_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.stream_frame.pack(pady=20)
        
        self.refresh_button = tk.Button(self.stream_frame, text="🔄 Refresh Songs", 
                                      command=self.stream_from_github,
                                      bg='#4a4a4a', fg='#ffffff',
                                      relief=tk.FLAT, padx=15, pady=5)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(self.stream_frame, text="🗑 Clear Playlist", 
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
        
        # Loading progress frame
        self.loading_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.loading_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.loading_label = tk.Label(self.loading_frame, text="🔍 Scanning music library...", 
                                    font=('Arial', 12), 
                                    fg='#ffffff', bg='#2b2b2b')
        self.loading_label.pack(pady=(0, 5))
        
        # Progress bar for scanning
        self.scan_progress_var = tk.DoubleVar()
        self.scan_progress_bar = ttk.Progressbar(self.loading_frame, 
                                               variable=self.scan_progress_var,
                                               maximum=100, length=700)
        self.scan_progress_bar.pack(pady=(0, 5))
        
        # Progress percentage label
        self.progress_percent_label = tk.Label(self.loading_frame, text="0%", 
                                             font=('Arial', 10, 'bold'), 
                                             fg='#00ff00', bg='#2b2b2b')
        self.progress_percent_label.pack()
        
        # Hide loading frame initially
        self.loading_frame.pack_forget()
        
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
        self.root.bind('<s>', lambda e: self.toggle_shuffle())
        self.root.bind('<S>', lambda e: self.toggle_shuffle())
        
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
            

            
    def stream_from_github(self):
        """Stream songs from GitHub repository with comprehensive scanning"""
        try:
            # Clear existing playlist
            self.clear_playlist()
            
            # Show loading interface
            self.show_loading_screen()
            
            # GitHub repository details
            repo_url = "https://github.com/justAleks0/MP3-Player"
            songs_path = "MP3 Player/Songs"
            
            # Get repository contents
            api_url = f"https://api.github.com/repos/justAleks0/MP3-Player/contents/{songs_path}"
            
            self.update_scan_progress(5, "🌐 Connecting to GitHub repository...")
            
            response = requests.get(api_url)
            if response.status_code == 200:
                contents = response.json()
                
                # First pass: Discover all files across all folders
                self.update_scan_progress(10, "📁 Discovering all music files...")
                all_files = self.discover_all_files(contents, songs_path)
                
                # Second pass: Extract metadata from all files
                self.update_scan_progress(20, "🔍 Scanning metadata from all files...")
                all_songs = self.extract_all_metadata(all_files)
                
                # Third pass: Group by artist and organize
                self.update_scan_progress(80, "🎵 Organizing songs by artist...")
                self.group_and_add_songs_with_progress(all_songs)
                
                self.update_scan_progress(100, "✅ Music library scan complete!")
                
                # Hide loading screen after a brief delay
                self.root.after(1500, self.hide_loading_screen)
                
            else:
                self.hide_loading_screen()
                messagebox.showerror("Error", f"Failed to access GitHub repository: {response.status_code}")
                
        except Exception as e:
            self.hide_loading_screen()
            messagebox.showerror("Error", f"Failed to stream from GitHub: {str(e)}")
            self.status_var.set("GitHub streaming failed")
    
    def show_loading_screen(self):
        """Show the loading progress interface"""
        self.loading_frame.pack(fill=tk.X, pady=(10, 0), before=self.playlist_frame)
        self.playlist_frame.pack_forget()
        
    def hide_loading_screen(self):
        """Hide the loading progress interface"""
        self.loading_frame.pack_forget()
        self.playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
    def update_scan_progress(self, percentage, message):
        """Update the progress bar and message"""
        self.scan_progress_var.set(percentage)
        self.progress_percent_label.config(text=f"{int(percentage)}%")
        self.loading_label.config(text=message)
        self.status_var.set(message)
        self.root.update()
        
    def discover_all_files(self, contents, base_path):
        """Recursively discover all MP3 files across all folders"""
        all_files = []
        
        def scan_directory(items, current_path):
            for item in items:
                if item['type'] == 'file' and item['name'].lower().endswith('.mp3'):
                    all_files.append({
                        'url': item['download_url'],
                        'name': item['name'],
                        'path': current_path,
                        'folder': os.path.basename(current_path)
                    })
                elif item['type'] == 'dir':
                    try:
                        subdir_url = f"https://api.github.com/repos/justAleks0/MP3-Player/contents/{current_path}/{item['name']}"
                        subdir_response = requests.get(subdir_url)
                        if subdir_response.status_code == 200:
                            subdir_contents = subdir_response.json()
                            scan_directory(subdir_contents, f"{current_path}/{item['name']}")
                    except Exception as e:
                        pass
        
        scan_directory(contents, base_path)
        return all_files
        
    def extract_all_metadata(self, all_files):
        """Extract metadata from all discovered files with progress tracking"""
        all_songs = []
        total_files = len(all_files)
        
        for i, file_info in enumerate(all_files):
            # Calculate progress (20% to 80% of total progress)
            progress = 20 + (i / total_files) * 60
            self.update_scan_progress(progress, f"🔍 Scanning: {file_info['name']} ({i+1}/{total_files})")
            
            metadata = self.get_streaming_metadata(file_info['url'], file_info['name'])
            
            # Add folder information to metadata for better organization
            metadata['folder'] = file_info['folder']
            metadata['file_path'] = file_info['path']
            
            all_songs.append({
                'url': file_info['url'],
                'name': file_info['name'],
                'metadata': metadata,
                'folder': file_info['folder']
            })
            
        return all_songs
        
    def group_and_add_songs_with_progress(self, songs):
        """Group songs by artist with progress tracking and comprehensive organization"""
        # Group songs by artist (across all folders)
        artist_groups = {}
        
        for song in songs:
            artist = song['metadata']['artist']
            if artist not in artist_groups:
                artist_groups[artist] = []
            artist_groups[artist].append(song)
        
        # Sort artists alphabetically
        sorted_artists = sorted(artist_groups.keys())
        
        # Update progress
        self.update_scan_progress(85, f"🎵 Organizing {len(sorted_artists)} artists...")
        
        # Add songs grouped by artist with separators
        total_artists = len(sorted_artists)
        for i, artist in enumerate(sorted_artists):
            # Update progress for each artist
            artist_progress = 85 + (i / total_artists) * 10
            self.update_scan_progress(artist_progress, f"🎵 Adding {artist}...")
            
            # Add artist separator
            separator_text = f"====={artist}====="
            self.playlist.append({'type': 'separator', 'text': separator_text})
            self.playlist_listbox.insert(tk.END, separator_text)
            
            # Sort songs within artist by title
            artist_songs = sorted(artist_groups[artist], key=lambda x: x['metadata']['title'])
            
            # Add songs for this artist
            for song in artist_songs:
                streaming_entry = {
                    'type': 'streaming',
                    'url': song['url'],
                    'name': song['name'],
                    'metadata': song['metadata'],
                    'folder': song['folder'],
                    'display_name': f"🌐 {song['metadata']['title']}"
                }
                
                # Add folder info if multiple folders exist for same artist
                if len([s for s in artist_groups[artist] if s['folder'] != song['folder']]) > 0:
                    streaming_entry['display_name'] = f"🌐 {song['metadata']['title']} [{song['folder']}]"
                
                self.playlist.append(streaming_entry)
                self.playlist_listbox.insert(tk.END, streaming_entry['display_name'])
        
        # Save original playlist order for shuffle functionality
        self.original_playlist = self.playlist.copy()
        
        # Final status update
        total_songs = sum(len(songs) for songs in artist_groups.values())
        self.status_var.set(f"✅ Loaded {total_songs} songs from {len(sorted_artists)} artists")
    
    def add_github_songs(self, contents, base_path):
        """Recursively add songs from GitHub repository"""
        songs_found = 0
        all_songs = []  # Collect all songs first
        
        for item in contents:
            if item['type'] == 'file' and item['name'].lower().endswith('.mp3'):
                # Found an MP3 file
                song_url = item['download_url']
                song_name = item['name']
                
                # Get metadata for the song
                metadata = self.get_streaming_metadata(song_url, song_name)
                all_songs.append({
                    'url': song_url,
                    'name': song_name,
                    'metadata': metadata
                })
                songs_found += 1
                
            elif item['type'] == 'dir':
                # Recursively explore subdirectories (artists)
                try:
                    subdir_url = f"https://api.github.com/repos/justAleks0/MP3-Player/contents/{base_path}/{item['name']}"
                    subdir_response = requests.get(subdir_url)
                    
                    if subdir_response.status_code == 200:
                        subdir_contents = subdir_response.json()
                        subdir_songs = self.add_github_songs(subdir_contents, f"{base_path}/{item['name']}")
                        songs_found += subdir_songs
                        
                except Exception as e:
                    self.status_var.set(f"Error accessing subdirectory {item['name']}: {str(e)}")
        
        # Group songs by artist and add to playlist
        if all_songs:
            self.group_and_add_songs(all_songs)
        
        if songs_found > 0:
            self.status_var.set(f"Added {songs_found} streaming songs from GitHub")
        else:
            messagebox.showwarning("No songs found", "No MP3 files found in the GitHub repository.")
            
        return songs_found
    
    def get_streaming_metadata(self, url, name):
        """Get metadata for streaming songs"""
        metadata = {
            'artist': 'Unknown Artist',
            'title': name.replace('.mp3', ''),
            'album': 'Unknown Album',
            'year': 'Unknown',
            'genre': 'Unknown',
            'duration': 'Unknown',
            'bitrate': 'Unknown',
            'filesize': 'Unknown'
        }
        
        try:
            # Download a small portion to get metadata
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Create temporary file for metadata extraction
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                # Download first 1MB for metadata
                chunk_size = 8192
                downloaded = 0
                max_download = 1024 * 1024  # 1MB
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if downloaded >= max_download:
                        break
                    temp_file.write(chunk)
                    downloaded += len(chunk)
                
                temp_file.flush()
                
                # Extract metadata
                try:
                    audio = MP3(temp_file.name)
                    
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
                
                except Exception as e:
                    pass
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
        except Exception as e:
            pass
        
        return metadata
    
    def group_and_add_songs(self, songs):
        """Group songs by artist and add to playlist with separators"""
        # Group songs by artist
        artist_groups = {}
        
        for song in songs:
            artist = song['metadata']['artist']
            if artist not in artist_groups:
                artist_groups[artist] = []
            artist_groups[artist].append(song)
        
        # Sort artists alphabetically
        sorted_artists = sorted(artist_groups.keys())
        
        # Add songs grouped by artist with separators
        for artist in sorted_artists:
            # Add artist separator
            separator_text = f"====={artist}====="
            self.playlist.append({'type': 'separator', 'text': separator_text})
            self.playlist_listbox.insert(tk.END, separator_text)
            
            # Add songs for this artist
            for song in artist_groups[artist]:
                streaming_entry = {
                    'type': 'streaming',
                    'url': song['url'],
                    'name': song['name'],
                    'metadata': song['metadata'],
                    'display_name': f"🌐 {song['metadata']['title']}"
                }
                
                self.playlist.append(streaming_entry)
                self.playlist_listbox.insert(tk.END, streaming_entry['display_name'])
    
    def add_streaming_song(self, url, name):
        """Add a streaming song to the playlist"""
        # Create a special entry for streaming songs
        streaming_entry = {
            'type': 'streaming',
            'url': url,
            'name': name,
            'display_name': f"🌐 {name}"
        }
        
        # Add to playlist
        self.playlist.append(streaming_entry)
        self.playlist_listbox.insert(tk.END, streaming_entry['display_name'])
        
    def stream_directly_from_url(self, url, name):
        """Stream directly from URL without any file creation"""
        try:
            # For true streaming, we need to use pygame's URL support
            # However, pygame.mixer doesn't support direct URL streaming
            # So we'll use a minimal temporary file that gets deleted immediately after use
            
            self.status_var.set(f"Streaming {name}...")
            self.root.update()
            
            # Create a minimal temp file that will be deleted after playback
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Stream the file in chunks
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(temp_file.name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Return the temp file path (will be cleaned up later)
            return temp_file.name
            
        except Exception as e:
            self.status_var.set(f"Streaming failed: {str(e)}")
            return None
            
    def display_streaming_metadata(self, metadata):
        """Display metadata for streaming songs"""
        for key, label in self.metadata_labels.items():
            if key in metadata:
                label.config(text=metadata[key])
            else:
                label.config(text="N/A")
    

            
    def clear_playlist(self):
        self.stop()
        self.playlist.clear()
        self.original_playlist.clear()
        self.playlist_listbox.delete(0, tk.END)
        self.current_track = None
        self.current_index = 0
        self.track_label.config(text="No track selected")
        
        # Reset shuffle state
        self.is_shuffled = False
        self.shuffle_button.config(bg='#4a4a4a', text='🔀')
        
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
            current_item = self.playlist[self.current_index]
            self.playlist_listbox.selection_clear(0, tk.END)
            self.playlist_listbox.selection_set(self.current_index)
            self.playlist_listbox.see(self.current_index)
            
            try:
                # Handle separators - skip to next track
                if isinstance(current_item, dict) and current_item.get('type') == 'separator':
                    self.next_track()
                    return
                
                # Handle streaming songs only (no local files)
                if isinstance(current_item, dict) and current_item.get('type') == 'streaming':
                    # Stream directly from URL without caching
                    streamed_file = self.stream_directly_from_url(current_item['url'], current_item['name'])
                    if streamed_file:
                        self.current_track = streamed_file
                        display_name = current_item['metadata']['title']
                        artist = current_item['metadata']['artist']
                        self.track_label.config(text=f"Now playing: 🌐 {artist} - {display_name}")
                        self.status_var.set(f"Playing: {display_name}")
                    else:
                        self.status_var.set("Failed to stream song")
                        return
                else:
                    # No local files supported - skip
                    self.status_var.set("Only streaming songs supported")
                    return
                
                pygame.mixer.music.load(self.current_track)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.play_button.config(text="⏸")
                
                # Display metadata for streaming songs
                self.display_streaming_metadata(current_item['metadata'])
                self.artwork_label.configure(image=self.default_artwork)
                self.artwork_label.image = self.default_artwork
                
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
        self.cleanup_temp_files()
        self.status_var.set("Stopped")
        
    def next_track(self):
        if self.playlist:
            self.cleanup_temp_files()
            self.current_index = (self.current_index + 1) % len(self.playlist)
            
            # Skip separators
            while (self.current_index < len(self.playlist) and 
                   isinstance(self.playlist[self.current_index], dict) and 
                   self.playlist[self.current_index].get('type') == 'separator'):
                self.current_index = (self.current_index + 1) % len(self.playlist)
            
            self.play_current_track()
            
    def previous_track(self):
        if self.playlist:
            self.cleanup_temp_files()
            self.current_index = (self.current_index - 1) % len(self.playlist)
            
            # Skip separators
            while (self.current_index >= 0 and 
                   isinstance(self.playlist[self.current_index], dict) and 
                   self.playlist[self.current_index].get('type') == 'separator'):
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
        
    def toggle_shuffle(self):
        """Toggle shuffle mode on/off"""
        import random
        
        if not self.is_shuffled:
            # Enable shuffle
            self.is_shuffled = True
            self.shuffle_button.config(bg='#ff6b35', text='🔀')  # Orange background when active
            
            # Save original playlist order
            self.original_playlist = self.playlist.copy()
            
            # Create shuffled playlist while preserving separators
            songs_only = [item for item in self.playlist if isinstance(item, dict) and item.get('type') == 'streaming']
            separators = [item for item in self.playlist if isinstance(item, dict) and item.get('type') == 'separator']
            
            # Shuffle only the songs
            random.shuffle(songs_only)
            
            # Create new shuffled playlist with songs only (no separators in shuffle mode)
            self.playlist = songs_only
            
            # Update the listbox display
            self.refresh_playlist_display()
            
            # Adjust current index if needed
            if self.current_track:
                try:
                    # Find the current track in the new shuffled playlist
                    for i, item in enumerate(self.playlist):
                        if (isinstance(item, dict) and item.get('type') == 'streaming' and 
                            hasattr(self, 'current_track') and 
                            item.get('url') == getattr(self.current_item, 'get', lambda x: None)('url')):
                            self.current_index = i
                            break
                except:
                    self.current_index = 0
            
            self.status_var.set("🔀 Shuffle enabled - Playing songs in random order")
            
        else:
            # Disable shuffle
            self.is_shuffled = False
            self.shuffle_button.config(bg='#4a4a4a', text='🔀')  # Return to normal background
            
            # Restore original playlist order
            if self.original_playlist:
                self.playlist = self.original_playlist.copy()
                self.refresh_playlist_display()
                
                # Try to find current track in original playlist
                if self.current_track:
                    try:
                        for i, item in enumerate(self.playlist):
                            if (isinstance(item, dict) and item.get('type') == 'streaming' and 
                                hasattr(self, 'current_item') and 
                                item.get('url') == getattr(self.current_item, 'get', lambda x: None)('url')):
                                self.current_index = i
                                break
                    except:
                        self.current_index = 0
            
            self.status_var.set("📋 Shuffle disabled - Playing songs in original order")
            
    def refresh_playlist_display(self):
        """Refresh the playlist display in the listbox"""
        self.playlist_listbox.delete(0, tk.END)
        
        for item in self.playlist:
            if isinstance(item, dict):
                if item.get('type') == 'separator':
                    self.playlist_listbox.insert(tk.END, item['text'])
                elif item.get('type') == 'streaming':
                    self.playlist_listbox.insert(tk.END, item['display_name'])
            else:
                # Handle any non-dict items (shouldn't happen in streaming mode)
                self.playlist_listbox.insert(tk.END, str(item))
        
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
                
    def cleanup_temp_files(self):
        """Clean up temporary streaming files"""
        try:
            if hasattr(self, 'current_track') and self.current_track:
                if os.path.exists(self.current_track) and 'tmp' in self.current_track:
                    os.unlink(self.current_track)
        except:
            pass
    
    def on_closing(self):
        self.cleanup_temp_files()
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
