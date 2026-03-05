window.__THEME_CONFIG__ = {
    tailwind: {
        theme: {
            extend: {
                colors: {
                    void: {
                        DEFAULT: '#080812',
                        50: '#0c0c1a',
                        100: '#101024',
                        200: '#181836',
                    },
                    warm: {
                        DEFAULT: '#00f0ff',
                        light: '#60fcff',
                        soft: 'rgba(0, 240, 255, 0.6)',
                        faint: 'rgba(0, 240, 255, 0.15)',
                        glow: 'rgba(0, 240, 255, 0.08)',
                    }
                },
                fontFamily: {
                    serif: ['Orbitron', 'Rajdhani', 'sans-serif'],
                    sans: ['Share Tech Mono', 'JetBrains Mono', 'monospace'],
                }
            }
        }
    },
    copy: {
        brand: 'DATASTREAM',
        addButton: 'Acquire',
        downloadTitle: 'Acquire from YouTube',
        downloadSubtitle: 'Input a YouTube feed URL to cache locally',
        downloadSubmit: 'Download',
        downloadSubmitting: 'Acquiring...',
        downloadsLabel: 'Queue',
        downloadingOne: 'acquiring',
        deleteTitle: 'Purge this file?',
        deleteMessage: 'The media file and all associated data will be permanently erased.',
        deleteButton: 'Purge',
        deleteCancel: 'Abort',
        itemSingular: 'file',
        itemPlural: 'files',
        emptyTitle: 'No data cached',
        emptyMessage: 'Download your first media file to populate the local cache',
        emptyAction: 'Acquire First File',
        saveToDevice: 'Export to Device',
        notesLabel: 'Log',
        notesPlaceholder: 'Enter notes, timestamps, observations...',
        favoriteAction: 'Pin',
        favoritedAction: 'Pinned',
        favoriteSymbol: '\u2605',
        unfavoriteSymbol: '\u2606',
        filterAll: 'All',
        filterFavorites: 'Pinned',
        backLabel: 'Index',
        revealLabel: 'Open in File Manager',
        revealLabelShort: 'Files',
    }
};
