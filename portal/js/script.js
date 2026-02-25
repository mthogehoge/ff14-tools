// FF14 Portal Scripts

document.addEventListener('DOMContentLoaded', () => {
    // Coming soon リンクのデフォルトアクション（ページ先頭へのスクロール等）を無効化する
    const comingSoonLink = document.getElementById('coming-soon-link');
    if (comingSoonLink) {
        comingSoonLink.addEventListener('click', (e) => {
            e.preventDefault();
        });
    }
});
