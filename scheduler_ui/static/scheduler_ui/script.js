function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('triggerBtn');
  const result = document.getElementById('result');

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    result.textContent = 'Triggering...';
    try {
      const res = await fetch('/trigger/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({action: 'test'})
      });

      const data = await res.json();
      if (data.success) {
        result.textContent = 'Success: ' + (data.result || 'triggered');
      } else {
        result.textContent = 'Error: ' + (data.error || 'unknown');
      }
    } catch (err) {
      result.textContent = 'Network error: ' + err;
    } finally {
      btn.disabled = false;
    }
  });
});
