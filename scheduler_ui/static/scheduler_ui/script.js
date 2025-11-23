function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Helper to convert datetime-local to ISO string (UTC)
function formatDateTimeLocal(dateTimeLocal) {
  // datetime-local gives us YYYY-MM-DDTHH:mm format (in user's local timezone)
  // We need to convert it to ISO format with UTC timezone
  // new Date() interprets the datetime-local value in the browser's timezone
  // toISOString() converts it to UTC
  const date = new Date(dateTimeLocal);
  return date.toISOString();
}

// Helper to get user's timezone
function getUserTimezone() {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('scheduleForm');
  const scheduleBtn = document.getElementById('scheduleBtn');
  const result = document.getElementById('result');
  const scheduledTimeInput = document.getElementById('scheduled_time');
  const timezoneDisplay = document.getElementById('timezone-display');

  // Display user's timezone
  const userTimezone = getUserTimezone();
  const timezoneOffset = -new Date().getTimezoneOffset() / 60;
  const offsetString = timezoneOffset >= 0 ? `UTC+${timezoneOffset}` : `UTC${timezoneOffset}`;
  timezoneDisplay.textContent = `${userTimezone} (${offsetString})`;

  // Set minimum datetime to now (prevent scheduling in the past)
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  scheduledTimeInput.min = now.toISOString().slice(0, 16);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    scheduleBtn.disabled = true;
    result.textContent = 'Scheduling message...';
    result.className = '';

    const phone = document.getElementById('phone').value.trim();
    const body = document.getElementById('body').value.trim();
    const scheduled_time = scheduledTimeInput.value;

    if (!phone || !body || !scheduled_time) {
      result.textContent = 'Error: All fields are required';
      result.className = 'error';
      scheduleBtn.disabled = false;
      return;
    }

    try {
      const res = await fetch('/trigger/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
          phone: phone,
          body: body,
          scheduled_time: formatDateTimeLocal(scheduled_time)
        })
      });

      const data = await res.json();
      if (data.success) {
        // Display the scheduled time in user's local timezone
        const scheduledDate = new Date(data.scheduled_time);
        const tz = getUserTimezone();
        const localTimeString = scheduledDate.toLocaleString(undefined, {
          timeZone: tz,
          dateStyle: 'full',
          timeStyle: 'long'
        });
        result.textContent = `Success! Message scheduled (ID: ${data.queued_id}). Will be sent at ${localTimeString} (${tz})`;
        result.className = 'success';
        form.reset();
        // Reset min time
        const newNow = new Date();
        newNow.setMinutes(newNow.getMinutes() - newNow.getTimezoneOffset());
        scheduledTimeInput.min = newNow.toISOString().slice(0, 16);
      } else {
        result.textContent = 'Error: ' + (data.error || 'unknown');
        result.className = 'error';
      }
    } catch (err) {
      result.textContent = 'Network error: ' + err;
      result.className = 'error';
    } finally {
      scheduleBtn.disabled = false;
    }
  });
});
