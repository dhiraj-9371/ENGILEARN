document.addEventListener('DOMContentLoaded', function () {
  const body = document.body;
  const toggle = document.getElementById('sidebarToggle');
  const backdrop = document.getElementById('sidebarBackdrop');

  if (toggle) {
    toggle.addEventListener('click', function () {
      body.classList.toggle('sidebar-open');
    });
  }
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      body.classList.remove('sidebar-open');
    });
  }

  document.querySelectorAll('input, select, textarea').forEach((el) => {
    if (el.type === 'radio' || el.type === 'checkbox' || el.type === 'hidden' || el.classList.contains('no-auto-style')) return;
    if (el.tagName === 'SELECT') {
      el.classList.add('form-select');
    } else {
      el.classList.add('form-control');
    }
  });

  document.querySelectorAll('input[type="password"]').forEach((input) => {
    if (input.closest('.password-toggle-wrap')) return;
    const wrap = document.createElement('div');
    wrap.className = 'password-toggle-wrap';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'password-toggle-btn';
    btn.innerHTML = '<i class="fa-regular fa-eye"></i>';
    btn.addEventListener('click', () => {
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      btn.innerHTML = isPassword ? '<i class="fa-regular fa-eye-slash"></i>' : '<i class="fa-regular fa-eye"></i>';
    });
    wrap.appendChild(btn);
  });

  const chartDataElement = document.getElementById('attendanceChartData');
  const chartCanvas = document.getElementById('attendanceChart');
  if (chartDataElement && chartCanvas && typeof Chart !== 'undefined') {
    try {
      const parsed = JSON.parse(chartDataElement.textContent.trim() || '[]');
      new Chart(chartCanvas, {
        type: 'doughnut',
        data: {
          labels: parsed.map(x => x.label),
          datasets: [{ data: parsed.map(x => x.value), borderWidth: 0 }],
        },
        options: {
          responsive: true,
          cutout: '68%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#4a5b7f', padding: 18, usePointStyle: true }
            }
          }
        }
      });
    } catch (err) {
      console.error('Chart rendering failed', err);
    }
  }

  const quizTimer = document.getElementById('quizTimer');
  const quizDuration = document.getElementById('quizDuration');
  const quizForm = document.getElementById('quizForm');
  if (quizTimer && quizDuration && quizForm) {
    let remaining = parseInt(quizDuration.value || '0', 10);
    const formatTime = (seconds) => {
      const min = String(Math.floor(seconds / 60)).padStart(2, '0');
      const sec = String(Math.max(seconds % 60, 0)).padStart(2, '0');
      return `${min}:${sec}`;
    };
    quizTimer.textContent = formatTime(remaining);
    const timerId = setInterval(() => {
      remaining -= 1;
      quizTimer.textContent = formatTime(remaining);
      if (remaining <= 0) {
        clearInterval(timerId);
        quizForm.submit();
      }
    }, 1000);
  }

  document.querySelectorAll('[data-copy-text]').forEach((button) => {
    button.addEventListener('click', async () => {
      const text = button.getAttribute('data-copy-text');
      try {
        await navigator.clipboard.writeText(text);
        const original = button.innerHTML;
        button.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
        setTimeout(() => { button.innerHTML = original; }, 1500);
      } catch (e) {
        console.error('Copy failed', e);
      }
    });
  });

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  };

  const lessonVideo = document.getElementById('lessonVideo');
  if (lessonVideo) {
    const statusUrl = lessonVideo.dataset.statusUrl;
    let lastSent = 0;
    let completionSent = false;

    const sendStatus = (progressSeconds, completed) => {
      const formData = new FormData();
      formData.append('progress_seconds', String(progressSeconds || 0));
      formData.append('completed', completed ? 'true' : 'false');
      return fetch(statusUrl, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
      }).catch((err) => console.error('Video status update failed', err));
    };

    lessonVideo.addEventListener('timeupdate', () => {
      const current = Math.floor(lessonVideo.currentTime || 0);
      if (current - lastSent >= 10) {
        lastSent = current;
        sendStatus(current, false);
      }
      const duration = lessonVideo.duration || 0;
      if (!completionSent && duration > 0 && current >= Math.max(duration - 2, 1)) {
        completionSent = true;
        sendStatus(current, true).then(() => {
          const badge = document.querySelector('.badge-soft.warning');
          if (badge) {
            badge.classList.remove('warning');
            badge.classList.add('success');
            badge.textContent = 'Viewed';
          }
        });
      }
    });
  }

  const manualWatchForm = document.getElementById('manualWatchForm');
  if (manualWatchForm) {
    manualWatchForm.addEventListener('submit', function (e) {
      e.preventDefault();
      fetch(manualWatchForm.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: new FormData(manualWatchForm),
      })
      .then((r) => r.json())
      .then(() => {
        const btn = manualWatchForm.querySelector('button');
        if (btn) {
          btn.textContent = 'Marked as watched';
          btn.disabled = true;
        }
      })
      .catch((err) => console.error(err));
    });
  }
});
