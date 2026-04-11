document.querySelectorAll('.img-zoom-container').forEach(function(container) {
    var thumb = container.querySelector('img');
    var overlay = container.querySelector('.img-zoom-overlay');
    if (!thumb || !overlay) { return; }
    thumb.addEventListener('click', function() {
        overlay.classList.add('active');
    });
    overlay.addEventListener('click', function() {
        overlay.classList.remove('active');
    });
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.img-zoom-overlay.active').forEach(function(ov) {
            ov.classList.remove('active');
        });
    }
});
