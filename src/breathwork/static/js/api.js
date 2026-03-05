const api = {
    async getVideos(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`/api/videos?${query}`);
        return res.json();
    },

    async getVideo(id) {
        const res = await fetch(`/api/videos/${id}`);
        return res.json();
    },

    async updateVideo(id, data) {
        const res = await fetch(`/api/videos/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return res.json();
    },

    async deleteVideo(id) {
        const res = await fetch(`/api/videos/${id}`, { method: 'DELETE' });
        return res.json();
    },

    async markWatched(id) {
        const res = await fetch(`/api/videos/${id}/watch`, { method: 'POST' });
        return res.json();
    },

    async startDownload(url) {
        const res = await fetch('/api/downloads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });
        return res.json();
    },

    async getDownloads() {
        const res = await fetch('/api/downloads');
        return res.json();
    },

    async revealInFinder(videoId) {
        await fetch('/api/system/reveal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId }),
        });
    },

    async getSystemInfo() {
        const res = await fetch('/api/system/info');
        return res.json();
    },
};
