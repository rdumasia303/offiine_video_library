function formatDuration(seconds) {
    if (!seconds) return '';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${m}:${String(s).padStart(2, '0')}`;
}

function formatSize(bytes) {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
    return `${mb.toFixed(0)} MB`;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        view: 'library',
        videos: [],
        currentVideo: null,
        searchQuery: '',
        showFavoritesOnly: false,
        downloads: [],
        showDownloadModal: false,
        downloadUrl: '',
        downloadSubmitting: false,
        toast: null,
        toastTimeout: null,
        systemInfo: null,
        notesSaved: false,
        notesSaveTimeout: null,
        confirmDelete: null,
        copy: window.__THEME_CONFIG__?.copy || {},

        async init() {
            await this.loadVideos();
            this.connectSSE();
            this.loadSystemInfo();
            setInterval(() => this.pollDownloads(), 3000);
        },

        async loadVideos() {
            this.videos = await api.getVideos();
        },

        async loadSystemInfo() {
            try { this.systemInfo = await api.getSystemInfo(); } catch (e) { }
        },

        connectSSE() {
            const source = new EventSource('/api/downloads/progress');
            source.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleProgress(data);
            };
            source.onerror = () => {
                setTimeout(() => this.connectSSE(), 5000);
                source.close();
            };
        },

        handleProgress(data) {
            const idx = this.downloads.findIndex(d => d.id === data.task_id);
            if (idx >= 0) {
                this._applyDownloadStatus(
                    this.downloads[idx], data.status, data.progress, data.error
                );
            }
        },

        _applyDownloadStatus(dl, status, progress, errorMsg) {
            const wasActive = ['pending', 'downloading', 'processing'].includes(dl.status);
            if (progress != null) dl.progress = progress;
            dl.status = status;
            if (dl.title == null && status === 'completed') dl.title = dl.url;

            if (wasActive && status === 'completed') {
                this.showToast('Download complete!', 'success');
                this.loadVideos();
                if (this.showDownloadModal && !this.downloadUrl.trim()) {
                    setTimeout(() => {
                        if (!this.downloadUrl.trim()) {
                            this.showDownloadModal = false;
                            this.downloads = [];
                        }
                    }, 1500);
                }
            } else if (wasActive && status === 'failed') {
                this.showToast('Download failed: ' + (errorMsg || 'Unknown error'), 'error');
            }
        },

        async pollDownloads() {
            const hasActive = this.downloads.some(d =>
                ['pending', 'downloading', 'processing'].includes(d.status)
            );
            if (!hasActive) return;

            try {
                const tasks = await api.getDownloads();
                for (const dl of this.downloads) {
                    const server = tasks.find(t => t.id === dl.id);
                    if (!server) continue;
                    this._applyDownloadStatus(dl, server.status, server.progress, server.error_message);
                    if (server.title) dl.title = server.title;
                }
            } catch (e) { /* network error during poll */ }
        },

        get filteredVideos() {
            let vids = this.videos;
            if (this.searchQuery) {
                const q = this.searchQuery.toLowerCase();
                vids = vids.filter(v =>
                    v.title.toLowerCase().includes(q) ||
                    (v.notes || '').toLowerCase().includes(q) ||
                    (v.channel || '').toLowerCase().includes(q)
                );
            }
            if (this.showFavoritesOnly) {
                vids = vids.filter(v => v.is_favorite);
            }
            return vids;
        },

        get activeDownloads() {
            return this.downloads.filter(d => d.status === 'downloading' || d.status === 'pending' || d.status === 'processing');
        },

        openPlayer(video) {
            this.currentVideo = { ...video };
            this.view = 'player';
            this.notesSaved = false;
            api.markWatched(video.id);
        },

        goToLibrary() {
            this.view = 'library';
            this.currentVideo = null;
            this.loadVideos();
        },

        async submitDownload() {
            if (!this.downloadUrl.trim()) return;
            this.downloadSubmitting = true;
            try {
                const task = await api.startDownload(this.downloadUrl.trim());
                this.downloads.unshift(task);
                this.downloadUrl = '';
                this.showToast('Download started!', 'success');
            } catch (e) {
                this.showToast(e.message || 'Failed to start download', 'error');
            }
            this.downloadSubmitting = false;
        },

        async saveNotes() {
            if (!this.currentVideo) return;
            await api.updateVideo(this.currentVideo.id, { notes: this.currentVideo.notes });
            this.notesSaved = true;
            clearTimeout(this.notesSaveTimeout);
            this.notesSaveTimeout = setTimeout(() => { this.notesSaved = false; }, 2000);
        },

        async toggleFavorite(video) {
            const updated = await api.updateVideo(video.id, { is_favorite: !video.is_favorite });
            if (this.currentVideo && this.currentVideo.id === video.id) {
                this.currentVideo.is_favorite = updated.is_favorite;
            }
            const idx = this.videos.findIndex(v => v.id === video.id);
            if (idx >= 0) this.videos[idx].is_favorite = updated.is_favorite;
        },

        async deleteVideo(video) {
            await api.deleteVideo(video.id);
            this.confirmDelete = null;
            this.showToast('Video deleted', 'success');
            if (this.currentVideo && this.currentVideo.id === video.id) {
                this.goToLibrary();
            }
            this.loadVideos();
        },

        async revealInFinder(video) {
            await api.revealInFinder(video.id);
            this.showToast('Opened in file manager', 'success');
        },

        showToast(message, type = 'info') {
            this.toast = { message, type };
            clearTimeout(this.toastTimeout);
            this.toastTimeout = setTimeout(() => { this.toast = null; }, 4000);
        },

        formatDuration,
        formatSize,
        formatDate,
    }));
});
