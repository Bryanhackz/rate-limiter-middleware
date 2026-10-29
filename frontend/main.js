document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btn-test');
    const output = document.getElementById('output');

    btn.addEventListener('click', async () => {
        try {
            const res = await fetch('/');
            if (res.ok) {
                output.innerHTML = `<span class="ok">200 OK: Request allowed.</span>`;
            } else if (res.status === 429) {
                const retry = res.headers.get('Retry-After');
                output.innerHTML = `<span class="blocked">429 TOO MANY REQUESTS: Blocked. Retry after ${retry}s.</span>`;
            }
        } catch (e) {
            output.textContent = "Network error";
        }
    });
});