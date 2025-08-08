# 🌐 GitHub Music Streamer - Web Version

A modern web-based music streaming application that streams MP3 files directly from your GitHub repository. Built with HTML5, CSS3, and vanilla JavaScript.

## 🚀 Features

### 🎵 **Core Functionality**
- **GitHub Streaming** - Stream MP3 files directly from your repository
- **Artist Grouping** - Automatically organizes songs by artist across all folders
- **Metadata Display** - Shows artist, title, album, year, genre, and more
- **Progress Tracking** - Real-time scanning progress with percentage display
- **Cross-Folder Organization** - Groups songs by artist regardless of folder structure

### 🎮 **Player Controls**
- **Play/Pause** - Standard playback controls
- **Previous/Next** - Navigate through tracks
- **Stop** - Stop playback and reset
- **Shuffle Mode** - Randomize playback order
- **Volume Control** - Adjustable volume slider
- **Progress Bar** - Visual progress with seek functionality

### ⌨️ **Keyboard Shortcuts**
- **Spacebar** - Play/Pause
- **Left Arrow** - Previous track
- **Right Arrow** - Next track
- **Up Arrow** - Volume up (+10%)
- **Down Arrow** - Volume down (-10%)
- **S** - Toggle shuffle mode

### 📱 **Modern Interface**
- **Dark Theme** - Professional dark UI design
- **Responsive Layout** - Works on desktop and mobile devices
- **Loading Animation** - Visual feedback during repository scanning
- **Status Updates** - Real-time information about current operations

## 🌐 How to Use

### **Option 1: Local Setup**
1. Download all files (`index.html`, `style.css`, `script.js`)
2. Open `index.html` in a modern web browser
3. The app will automatically start scanning your GitHub repository

### **Option 2: GitHub Pages**
1. Upload the files to a GitHub Pages repository
2. Enable GitHub Pages in repository settings
3. Access your music streamer at `https://yourusername.github.io/repository-name`

### **Option 3: Local Server**
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Then open http://localhost:8000
```

## 🔧 Configuration

### **Repository Setup**
The app is configured to stream from:
- **Repository**: `justAleks0/MP3-Player`
- **Path**: `MP3 Player/Songs`

To use with your own repository:
1. Edit `script.js`
2. Find the line: `const repoUrl = "https://api.github.com/repos/justAleks0/MP3-Player/contents/MP3 Player/Songs"`
3. Replace with your repository URL

### **Supported File Structure**
```
MP3 Player/Songs/
├── Artist 1/
│   ├── song1.mp3
│   └── song2.mp3
├── Artist 2/
│   └── song3.mp3
└── Live Recordings/
    └── Artist 1 - Live Song.mp3
```

## 🎵 Features in Detail

### **Cross-Folder Artist Grouping**
The app intelligently groups songs by artist metadata, not folder structure:
```
=====Artist Name=====
🌐 Song Title 1 [Studio Albums]
🌐 Song Title 2 [Live Recordings]
🌐 Song Title 3 [Studio Albums]
```

### **Comprehensive Scanning Process**
1. **5%** - 🌐 Connecting to GitHub repository
2. **10%** - 📁 Discovering all music files
3. **20-80%** - 🔍 Scanning metadata from files
4. **85-95%** - 🎵 Organizing songs by artist
5. **100%** - ✅ Scan complete

### **Shuffle Mode**
- **Orange Button** - Visual indicator when shuffle is active
- **Song-Only Mode** - Removes artist separators during shuffle
- **Random Order** - True randomization of track order
- **Easy Toggle** - Click button or press 'S' key

## 📱 Browser Compatibility

### **Supported Browsers**
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Edge 79+

### **Required Features**
- ES6+ JavaScript support
- Fetch API
- HTML5 Audio
- CSS Grid and Flexbox

## 🔧 Technical Details

### **Architecture**
- **Frontend Only** - Pure client-side application
- **GitHub API** - Uses GitHub's REST API for file discovery
- **HTML5 Audio** - Native browser audio playback
- **Responsive Design** - CSS Grid and Flexbox layout

### **File Structure**
```
HTML/MP3 Player/
├── index.html          # Main application file
├── style.css           # Styling and responsive design
├── script.js           # Core application logic
└── README_WEB.md       # This documentation
```

### **API Usage**
- **GitHub API** - Repository content discovery
- **CORS-Enabled** - Direct streaming from GitHub's CDN
- **Rate Limiting** - GitHub API limits apply (60 requests/hour for unauthenticated)

## 🚀 Deployment Options

### **Static Hosting**
- GitHub Pages
- Netlify
- Vercel
- Any static file host

### **Local Development**
- File:// protocol (limited CORS)
- Local HTTP server (recommended)
- Browser dev tools for debugging

## ⚡ Performance

### **Optimizations**
- **Efficient Scanning** - Progressive loading with visual feedback
- **Smart Caching** - Browser handles audio caching
- **Responsive UI** - Non-blocking operations
- **Memory Management** - Proper cleanup of audio resources

### **Limitations**
- **GitHub API Limits** - 60 requests/hour without authentication
- **CORS Restrictions** - Some browsers may require HTTPS
- **Audio Formats** - Limited to MP3 files only
- **File Size** - Large repositories may take longer to scan

## 🎯 Differences from Python Version

### **Web Advantages**
- **No Installation** - Runs in any modern browser
- **Cross-Platform** - Works on any device with a browser
- **Easy Sharing** - Can be hosted and shared via URL
- **Auto-Updates** - Changes reflect immediately

### **Python Advantages**
- **More Audio Formats** - Supports various audio formats
- **Advanced Metadata** - Better ID3 tag reading
- **Local File Support** - Can play local files
- **No API Limits** - No GitHub API restrictions

## 🔮 Future Enhancements

### **Planned Features**
- **Playlist Persistence** - Save playlists in browser storage
- **Repeat Modes** - Single track and playlist repeat
- **Equalizer** - Audio frequency adjustment
- **Search/Filter** - Find songs quickly
- **Dark/Light Theme** - Theme switching

### **Technical Improvements**
- **GitHub Authentication** - Increase API limits
- **Service Worker** - Offline capability
- **Web Audio API** - Advanced audio processing
- **PWA Support** - Install as mobile app

## 📄 License

This project is open source and available under the MIT License.

---

🎵 **Enjoy your music streaming experience!** 🎵
