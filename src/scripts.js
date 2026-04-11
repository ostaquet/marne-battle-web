document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.img-zoom-toggle:checked').forEach(function(cb) {
            cb.checked = false;
        });
    }
});
