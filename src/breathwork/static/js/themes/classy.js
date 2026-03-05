window.__THEME_CONFIG__ = {
    tailwind: {
        theme: {
            extend: {
                colors: {
                    void: {
                        DEFAULT: '#111111',
                        50: '#161616',
                        100: '#1a1a1a',
                        200: '#222222',
                    },
                    warm: {
                        DEFAULT: '#c4a46c',
                        light: '#d4b87c',
                        soft: 'rgba(196, 164, 108, 0.6)',
                        faint: 'rgba(196, 164, 108, 0.15)',
                        glow: 'rgba(196, 164, 108, 0.06)',
                    }
                },
                fontFamily: {
                    serif: ['Playfair Display', 'Georgia', 'serif'],
                    sans: ['Source Sans 3', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
                }
            }
        }
    },
    copy: {
        brand: 'collection',
        addButton: 'From YouTube',
        downloadTitle: 'Add from YouTube',
        downloadSubtitle: 'Paste a YouTube URL to add it to your collection',
        downloadSubmit: 'Add Video',
        downloadSubmitting: 'Adding...',
        downloadsLabel: 'Downloads',
        downloadingOne: 'downloading',
        deleteTitle: 'Remove this video?',
        deleteMessage: 'The video file and any notes will be permanently deleted.',
        deleteButton: 'Delete',
        deleteCancel: 'Cancel',
        itemSingular: 'video',
        itemPlural: 'videos',
        emptyTitle: 'Your collection is empty',
        emptyMessage: 'Add your first video to start building your library',
        emptyAction: 'Add Your First Video',
        saveToDevice: 'Save to Device',
        notesLabel: 'Notes',
        notesPlaceholder: 'Add your notes here...',
        favoriteAction: 'Favorite',
        favoritedAction: 'Favorited',
        favoriteSymbol: '\u2726',
        unfavoriteSymbol: '\u2727',
        filterAll: 'All',
        filterFavorites: 'Favorites',
        backLabel: 'Library',
        revealLabel: 'Show in File Manager',
        revealLabelShort: 'Files',
    }
};
