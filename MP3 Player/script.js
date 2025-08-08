// GitHub Music Streamer Web Application
class GitHubMusicStreamer {
    constructor() {
        this.playlist = [];
        this.originalPlaylist = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.isPaused = false;
        this.isShuffled = false;
        this.audioPlayer = document.getElementById('audioPlayer');
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        
        // Auto-fetch songs on startup
        setTimeout(() => this.autoFetchSongs(), 1000);
    }
    
    initializeElements() {
        // Control elements
        this.playBtn = document.getElementById('playBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.shuffleBtn = document.getElementById('shuffleBtn');
        
        // Display elements
        this.trackTitle = document.getElementById('trackTitle');
        this.playlist = document.getElementById('playlist');
        this.statusText = document.getElementById('statusText');
        
        // Progress elements
        this.progressBar = document.getElementById('progressBar');
        this.progressFill = document.getElementById('progressFill');
        this.currentTime = document.getElementById('currentTime');
        this.totalTime = document.getElementById('totalTime');
        
        // Volume elements
        this.volumeSlider = document.getElementById('volumeSlider');
        this.volumeLabel = document.getElementById('volumeLabel');
        
        // Loading elements
        this.loadingScreen = document.getElementById('loadingScreen');
        this.loadingText = document.getElementById('loadingText');
        this.scanProgressFill = document.getElementById('scanProgressFill');
        this.scanProgressPercent = document.getElementById('scanProgressPercent');
        
        // Action buttons
        this.refreshBtn = document.getElementById('refreshBtn');
        this.clearBtn = document.getElementById('clearBtn');
        
        // Metadata elements
        this.metaArtist = document.getElementById('metaArtist');
        this.metaTitle = document.getElementById('metaTitle');
        this.metaAlbum = document.getElementById('metaAlbum');
        this.metaYear = document.getElementById('metaYear');
        this.metaGenre = document.getElementById('metaGenre');
        this.metaDuration = document.getElementById('metaDuration');
        this.metaBitrate = document.getElementById('metaBitrate');
        this.metaFilesize = document.getElementById('metaFilesize');
    }
    
    setupEventListeners() {
        // Control buttons
        this.playBtn.addEventListener('click', () => this.playPause());
        this.stopBtn.addEventListener('click', () => this.stop());
        this.prevBtn.addEventListener('click', () => this.previousTrack());
        this.nextBtn.addEventListener('click', () => this.nextTrack());
        this.shuffleBtn.addEventListener('click', () => this.toggleShuffle());
        
        // Action buttons
        this.refreshBtn.addEventListener('click', () => this.streamFromGitHub());
        this.clearBtn.addEventListener('click', () => this.clearPlaylist());
        
        // Volume control
        this.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
        
        // Progress bar
        this.progressBar.addEventListener('click', (e) => this.seek(e));
        
        // Audio player events
        this.audioPlayer.addEventListener('loadedmetadata', () => this.updateDuration());
        this.audioPlayer.addEventListener('timeupdate', () => this.updateProgress());
        this.audioPlayer.addEventListener('ended', () => this.nextTrack());
        this.audioPlayer.addEventListener('error', (e) => this.handleAudioError(e));
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case ' ':
                    e.preventDefault();
                    this.playPause();
                    break;
                case 'ArrowLeft':
                    this.previousTrack();
                    break;
                case 'ArrowRight':
                    this.nextTrack();
                    break;
                case 'ArrowUp':
                    this.volumeUp();
                    break;
                case 'ArrowDown':
                    this.volumeDown();
                    break;
                case 's':
                case 'S':
                    this.toggleShuffle();
                    break;
            }
        });
    }
    
    autoFetchSongs() {
        this.statusText.textContent = "🌐 Auto-loading songs from GitHub...";
        this.streamFromGitHub();
    }
    
    async streamFromGitHub() {
        try {
            this.clearPlaylist();
            this.showLoadingScreen();
            
            const repoUrl = "https://api.github.com/repos/justAleks0/MP3-Player/contents/MP3 Player/Songs";
            
            this.updateScanProgress(5, "🌐 Connecting to GitHub repository...");
            
            const response = await fetch(repoUrl);
            if (!response.ok) {
                throw new Error(`GitHub API error: ${response.status}`);
            }
            
            const contents = await response.json();
            
            this.updateScanProgress(10, "📁 Discovering all music files...");
            const allFiles = await this.discoverAllFiles(contents, "MP3 Player/Songs");
            
            this.updateScanProgress(20, "🔍 Scanning metadata from all files...");
            const allSongs = await this.extractAllMetadata(allFiles);
            
            this.updateScanProgress(80, "🎵 Organizing songs by artist...");
            this.groupAndAddSongs(allSongs);
            
            this.updateScanProgress(100, "✅ Music library scan complete!");
            
            setTimeout(() => this.hideLoadingScreen(), 1500);
            
        } catch (error) {
            this.hideLoadingScreen();
            console.error('Failed to stream from GitHub:', error);
            this.statusText.textContent = `Error: ${error.message}`;
        }
    }
    
    async discoverAllFiles(contents, basePath) {
        const allFiles = [];
        
        const scanDirectory = async (items, currentPath) => {
            for (const item of items) {
                if (item.type === 'file' && item.name.toLowerCase().endsWith('.mp3')) {
                    allFiles.push({
                        url: item.download_url,
                        name: item.name,
                        path: currentPath,
                        folder: currentPath.split('/').pop()
                    });
                } else if (item.type === 'dir') {
                    try {
                        const subdirUrl = `https://api.github.com/repos/justAleks0/MP3-Player/contents/${currentPath}/${item.name}`;
                        const subdirResponse = await fetch(subdirUrl);
                        if (subdirResponse.ok) {
                            const subdirContents = await subdirResponse.json();
                            await scanDirectory(subdirContents, `${currentPath}/${item.name}`);
                        }
                    } catch (error) {
                        console.error(`Error scanning directory ${item.name}:`, error);
                    }
                }
            }
        };
        
        await scanDirectory(contents, basePath);
        return allFiles;
    }
    
    async extractAllMetadata(allFiles) {
        const allSongs = [];
        const totalFiles = allFiles.length;
        
        for (let i = 0; i < allFiles.length; i++) {
            const fileInfo = allFiles[i];
            const progress = 20 + (i / totalFiles) * 60;
            this.updateScanProgress(progress, `🔍 Scanning: ${fileInfo.name} (${i+1}/${totalFiles})`);
            
            const metadata = this.getBasicMetadata(fileInfo.name);
            metadata.folder = fileInfo.folder;
            metadata.file_path = fileInfo.path;
            
            allSongs.push({
                url: fileInfo.url,
                name: fileInfo.name,
                metadata: metadata,
                folder: fileInfo.folder
            });
        }
        
        return allSongs;
    }
    
    getBasicMetadata(filename) {
        // Basic metadata extraction from filename
        const nameWithoutExt = filename.replace('.mp3', '');
        const parts = nameWithoutExt.split(' - ');
        
        return {
            artist: parts.length > 1 ? parts[0] : 'Unknown Artist',
            title: parts.length > 1 ? parts.slice(1).join(' - ') : nameWithoutExt,
            album: 'Unknown Album',
            year: 'Unknown',
            genre: 'Unknown',
            duration: 'Unknown',
            bitrate: 'Unknown',
            filesize: 'Unknown'
        };
    }
    
    groupAndAddSongs(songs) {
        // Group songs by artist
        const artistGroups = {};
        
        for (const song of songs) {
            const artist = song.metadata.artist;
            if (!artistGroups[artist]) {
                artistGroups[artist] = [];
            }
            artistGroups[artist].push(song);
        }
        
        // Sort artists alphabetically
        const sortedArtists = Object.keys(artistGroups).sort();
        
        this.updateScanProgress(85, `🎵 Organizing ${sortedArtists.length} artists...`);
        
        // Add songs grouped by artist with separators
        this.playlist = [];
        for (let i = 0; i < sortedArtists.length; i++) {
            const artist = sortedArtists[i];
            const artistProgress = 85 + (i / sortedArtists.length) * 10;
            this.updateScanProgress(artistProgress, `🎵 Adding ${artist}...`);
            
            // Add artist separator
            const separatorText = `=====${artist}=====`;
            this.playlist.push({ type: 'separator', text: separatorText });
            
            // Sort songs within artist by title
            const artistSongs = artistGroups[artist].sort((a, b) => 
                a.metadata.title.localeCompare(b.metadata.title)
            );
            
            // Add songs for this artist
            for (const song of artistSongs) {
                const hasMultipleFolders = artistGroups[artist].some(s => s.folder !== song.folder);
                const displayName = hasMultipleFolders ? 
                    `🌐 ${song.metadata.title} [${song.folder}]` : 
                    `🌐 ${song.metadata.title}`;
                
                this.playlist.push({
                    type: 'streaming',
                    url: song.url,
                    name: song.name,
                    metadata: song.metadata,
                    folder: song.folder,
                    displayName: displayName
                });
            }
        }
        
        // Save original playlist and update display
        this.originalPlaylist = [...this.playlist];
        this.refreshPlaylistDisplay();
        
        const totalSongs = songs.length;
        this.statusText.textContent = `✅ Loaded ${totalSongs} songs from ${sortedArtists.length} artists`;
    }
    
    refreshPlaylistDisplay() {
        this.playlist.innerHTML = '';
        
        this.playlist.forEach((item, index) => {
            const playlistItem = document.createElement('div');
            playlistItem.className = 'playlist-item';
            
            if (item.type === 'separator') {
                playlistItem.className += ' separator';
                playlistItem.textContent = item.text;
            } else if (item.type === 'streaming') {
                playlistItem.textContent = item.displayName;
                playlistItem.addEventListener('click', () => this.playTrackAtIndex(index));
                
                if (index === this.currentIndex) {
                    playlistItem.className += ' selected';
                }
            }
            
            this.playlist.appendChild(playlistItem);
        });
    }
    
    playTrackAtIndex(index) {
        this.currentIndex = index;
        this.playCurrentTrack();
    }
    
    playCurrentTrack() {
        if (this.currentIndex >= 0 && this.currentIndex < this.playlist.length) {
            const currentItem = this.playlist[this.currentIndex];
            
            // Skip separators
            if (currentItem.type === 'separator') {
                this.nextTrack();
                return;
            }
            
            if (currentItem.type === 'streaming') {
                this.audioPlayer.src = currentItem.url;
                this.audioPlayer.load();
                
                const playPromise = this.audioPlayer.play();
                if (playPromise !== undefined) {
                    playPromise.then(() => {
                        this.isPlaying = true;
                        this.isPaused = false;
                        this.playBtn.textContent = '⏸';
                        
                        this.displayMetadata(currentItem.metadata);
                        this.trackTitle.textContent = `Now playing: 🌐 ${currentItem.metadata.artist} - ${currentItem.metadata.title}`;
                        this.statusText.textContent = `Playing: ${currentItem.metadata.title}`;
                        
                        this.refreshPlaylistDisplay();
                    }).catch(error => {
                        console.error('Playback failed:', error);
                        this.statusText.textContent = 'Failed to stream song';
                    });
                }
            }
        }
    }
    
    playPause() {
        if (!this.audioPlayer.src) {
            if (this.playlist.length > 0) {
                this.playCurrentTrack();
            }
            return;
        }
        
        if (this.isPlaying && !this.isPaused) {
            this.audioPlayer.pause();
            this.isPaused = true;
            this.playBtn.textContent = '▶';
            this.statusText.textContent = 'Paused';
        } else if (this.isPaused) {
            this.audioPlayer.play();
            this.isPaused = false;
            this.playBtn.textContent = '⏸';
            this.statusText.textContent = 'Playing';
        } else {
            this.playCurrentTrack();
        }
    }
    
    stop() {
        this.audioPlayer.pause();
        this.audioPlayer.currentTime = 0;
        this.isPlaying = false;
        this.isPaused = false;
        this.playBtn.textContent = '▶';
        this.progressFill.style.width = '0%';
        this.currentTime.textContent = '00:00';
        this.statusText.textContent = 'Stopped';
    }
    
    nextTrack() {
        if (this.playlist.length > 0) {
            do {
                this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
            } while (this.playlist[this.currentIndex].type === 'separator' && this.currentIndex !== 0);
            
            this.playCurrentTrack();
        }
    }
    
    previousTrack() {
        if (this.playlist.length > 0) {
            do {
                this.currentIndex = (this.currentIndex - 1 + this.playlist.length) % this.playlist.length;
            } while (this.playlist[this.currentIndex].type === 'separator' && this.currentIndex !== this.playlist.length - 1);
            
            this.playCurrentTrack();
        }
    }
    
    toggleShuffle() {
        if (!this.isShuffled) {
            // Enable shuffle
            this.isShuffled = true;
            this.shuffleBtn.classList.add('active');
            
            // Save original playlist
            this.originalPlaylist = [...this.playlist];
            
            // Create shuffled playlist (songs only)
            const songsOnly = this.playlist.filter(item => item.type === 'streaming');
            
            // Shuffle the songs
            for (let i = songsOnly.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [songsOnly[i], songsOnly[j]] = [songsOnly[j], songsOnly[i]];
            }
            
            this.playlist = songsOnly;
            this.refreshPlaylistDisplay();
            
            this.statusText.textContent = '🔀 Shuffle enabled - Playing songs in random order';
        } else {
            // Disable shuffle
            this.isShuffled = false;
            this.shuffleBtn.classList.remove('active');
            
            // Restore original playlist
            if (this.originalPlaylist.length > 0) {
                this.playlist = [...this.originalPlaylist];
                this.refreshPlaylistDisplay();
            }
            
            this.statusText.textContent = '📋 Shuffle disabled - Playing songs in original order';
        }
    }
    
    clearPlaylist() {
        this.stop();
        this.playlist = [];
        this.originalPlaylist = [];
        this.playlist.innerHTML = '';
        this.currentIndex = 0;
        this.trackTitle.textContent = 'No track selected';
        
        // Reset shuffle state
        this.isShuffled = false;
        this.shuffleBtn.classList.remove('active');
        
        // Clear metadata
        this.clearMetadata();
        
        this.statusText.textContent = 'Playlist cleared';
    }
    
    displayMetadata(metadata) {
        this.metaArtist.textContent = metadata.artist || 'N/A';
        this.metaTitle.textContent = metadata.title || 'N/A';
        this.metaAlbum.textContent = metadata.album || 'N/A';
        this.metaYear.textContent = metadata.year || 'N/A';
        this.metaGenre.textContent = metadata.genre || 'N/A';
        this.metaDuration.textContent = metadata.duration || 'N/A';
        this.metaBitrate.textContent = metadata.bitrate || 'N/A';
        this.metaFilesize.textContent = metadata.filesize || 'N/A';
    }
    
    clearMetadata() {
        const metadataElements = [
            this.metaArtist, this.metaTitle, this.metaAlbum, this.metaYear,
            this.metaGenre, this.metaDuration, this.metaBitrate, this.metaFilesize
        ];
        
        metadataElements.forEach(element => {
            element.textContent = 'N/A';
        });
    }
    
    setVolume(value) {
        this.audioPlayer.volume = value / 100;
        this.volumeLabel.textContent = `${value}%`;
    }
    
    volumeUp() {
        const currentVolume = this.volumeSlider.value;
        const newVolume = Math.min(100, parseInt(currentVolume) + 10);
        this.volumeSlider.value = newVolume;
        this.setVolume(newVolume);
    }
    
    volumeDown() {
        const currentVolume = this.volumeSlider.value;
        const newVolume = Math.max(0, parseInt(currentVolume) - 10);
        this.volumeSlider.value = newVolume;
        this.setVolume(newVolume);
    }
    
    seek(event) {
        if (this.audioPlayer.src && this.audioPlayer.duration) {
            const rect = this.progressBar.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const percentage = clickX / rect.width;
            this.audioPlayer.currentTime = percentage * this.audioPlayer.duration;
        }
    }
    
    updateProgress() {
        if (this.audioPlayer.duration) {
            const percentage = (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100;
            this.progressFill.style.width = `${percentage}%`;
            
            const current = this.formatTime(this.audioPlayer.currentTime);
            this.currentTime.textContent = current;
        }
    }
    
    updateDuration() {
        if (this.audioPlayer.duration) {
            const total = this.formatTime(this.audioPlayer.duration);
            this.totalTime.textContent = total;
        }
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    handleAudioError(event) {
        console.error('Audio error:', event);
        this.statusText.textContent = 'Error playing audio file';
    }
    
    showLoadingScreen() {
        this.loadingScreen.style.display = 'flex';
        document.getElementById('playlistContainer').style.display = 'none';
    }
    
    hideLoadingScreen() {
        this.loadingScreen.style.display = 'none';
        document.getElementById('playlistContainer').style.display = 'block';
    }
    
    updateScanProgress(percentage, message) {
        this.scanProgressFill.style.width = `${percentage}%`;
        this.scanProgressPercent.textContent = `${Math.round(percentage)}%`;
        this.loadingText.textContent = message;
        this.statusText.textContent = message;
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new GitHubMusicStreamer();
});
