function copyToClipboard(url) {
    navigator.clipboard.writeText(url).then(() => {
        showToast('URL copied to clipboard: ' + url);
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.getElementById('copyButton');

    if (copyButton) {
        copyButton.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            copyToClipboard(url);
        });
    }
});
