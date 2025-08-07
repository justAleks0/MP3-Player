# 🎵 Modern MP3 Player

A beautiful and feature-rich MP3 player built with Python, featuring a modern dark theme GUI and comprehensive playback controls.

## Features

- 🎵 **Modern Dark UI** - Sleek dark theme with intuitive controls
- 📁 **File & Folder Support** - Open individual MP3 files or entire folders
- 📋 **Playlist Management** - Build and manage playlists with drag-and-drop support
- ⏯️ **Full Playback Controls** - Play, pause, stop, next, previous
- 🔊 **Volume Control** - Adjustable volume with visual slider
- ⌨️ **Keyboard Shortcuts** - Space (play/pause), Arrow keys (navigation/volume)
- 📊 **Progress Tracking** - Visual progress bar and time display
- ⚙️ **Settings Persistence** - Remembers volume settings between sessions
- 🎨 **Responsive Design** - Clean, modern interface

## Installation

1. **Install Python** (3.7 or higher)
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Player

```bash
python mp3_player.py
```

### Controls

#### Mouse Controls
- **Play/Pause Button** - Start or pause playback
- **Previous/Next Buttons** - Navigate between tracks
- **Stop Button** - Stop playback and reset
- **Volume Slider** - Adjust volume (0-100%)
- **Progress Bar** - Click to seek (limited support)
- **Playlist** - Double-click any track to play it

#### Keyboard Shortcuts
- **Space** - Play/Pause
- **Left Arrow** - Previous track
- **Right Arrow** - Next track
- **Up Arrow** - Volume up (+10%)
- **Down Arrow** - Volume down (-10%)

#### File Operations
- **📁 Open File** - Select individual MP3 files
- **📂 Open Folder** - Add all MP3 files from a folder
- **🗑 Clear Playlist** - Remove all tracks from playlist

## Features in Detail

### Playlist Management
- Add individual MP3 files or entire folders
- Automatic sorting of files
- Visual playlist with scrollable interface
- Double-click to play any track
- Clear entire playlist with one click

### Audio Playback
- Supports standard MP3 files
- Smooth play/pause transitions
- Automatic track progression
- Volume control with visual feedback
- Progress tracking with time display

### User Interface
- Dark theme for easy viewing
- Modern button designs with emoji icons
- Responsive layout that adapts to window size
- Status bar with current operation feedback
- Professional typography and spacing

### Settings
- Volume settings are automatically saved
- Settings persist between application sessions
- Clean shutdown with proper resource cleanup

## Technical Details

- **GUI Framework**: tkinter (built-in Python)
- **Audio Engine**: pygame.mixer
- **File Handling**: pathlib and os modules
- **Threading**: Background progress updates
- **Data Persistence**: JSON settings storage

## Troubleshooting

### Common Issues

1. **"No module named 'pygame'"**
   - Run: `pip install pygame`

2. **Audio not playing**
   - Check if your system has audio drivers installed
   - Ensure MP3 files are not corrupted
   - Try different MP3 files

3. **Interface looks different**
   - This is normal on different operating systems
   - The dark theme should still be visible

### Supported Formats
- MP3 files (.mp3)
- Both uppercase and lowercase extensions supported

## Development

The player is built with modular design:
- `MP3Player` class handles all functionality
- UI components are organized in logical sections
- Threading is used for non-blocking progress updates
- Settings are managed through JSON persistence

## Future Enhancements

Potential improvements could include:
- Support for more audio formats (WAV, FLAC, etc.)
- Audio visualization
- Equalizer controls
- Playlist save/load functionality
- Shuffle and repeat modes
- Better seek functionality with actual file duration

## License

This project is open source and available under the MIT License.

---

Enjoy your music! 🎶
