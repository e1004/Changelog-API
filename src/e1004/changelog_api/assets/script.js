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
