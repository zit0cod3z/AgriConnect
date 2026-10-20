/* =====================================================
   AgroConnect — Frontend JS helpers
   ===================================================== */

(function () {
  'use strict';

  /* ── CSRF helper for AJAX POST ── */
  function getCookie(name) {
    var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : null;
  }

  /* ── Notification unread count polling ── */
  var notifBadge = document.getElementById('notif-count');
  if (notifBadge) {
    function pollNotifications() {
      fetch('/notifications/unread-count/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var count = data.count || 0;
          notifBadge.textContent = count;
          notifBadge.style.display = count > 0 ? 'flex' : 'none';
        })
        .catch(function () {});
    }
    pollNotifications();
    setInterval(pollNotifications, 30000);
  }

  /* ── Mark notification read (AJAX) ── */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-mark-read]');
    if (!btn) return;
    var notifId = btn.getAttribute('data-mark-read');
    fetch('/notifications/mark-read/' + notifId + '/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var row = btn.closest('.notif-item');
        if (row) row.classList.remove('unread');
        if (notifBadge) {
          notifBadge.textContent = data.count;
          notifBadge.style.display = data.count > 0 ? 'flex' : 'none';
        }
      })
      .catch(function () {});
  });

  /* ── Story like (AJAX) ── */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-like-story]');
    if (!btn) return;
    var storyId = btn.getAttribute('data-like-story');
    fetch('/stories/' + storyId + '/like/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var counter = document.getElementById('like-count-' + storyId);
        if (counter) counter.textContent = data.like_count;
        btn.disabled = true;
        btn.textContent = '♥ Liked';
      })
      .catch(function () {});
  });

  /* ── Offer / negotiation countdown timers ── */
  function updateCountdown(el) {
    var expiry = new Date(el.getAttribute('data-expires'));
    var diff = expiry - new Date();
    if (diff <= 0) {
      el.textContent = 'Expired';
      el.classList.add('text-danger');
      return;
    }
    var h = Math.floor(diff / 3600000);
    var m = Math.floor((diff % 3600000) / 60000);
    el.textContent = h + 'h ' + m + 'm remaining';
  }

  var timers = document.querySelectorAll('[data-expires]');
  timers.forEach(function (el) {
    updateCountdown(el);
    setInterval(function () { updateCountdown(el); }, 60000);
  });

  /* ── Group-buy progress bar live ── */
  var progressBars = document.querySelectorAll('.progress-agro .progress-bar');
  progressBars.forEach(function (bar) {
    var pct = parseFloat(bar.getAttribute('aria-valuenow')) || 0;
    bar.style.width = Math.min(pct, 100) + '%';
  });

  /* ── Image preview on file input ── */
  var imgInput = document.getElementById('id_images');
  if (imgInput) {
    imgInput.addEventListener('change', function () {
      var preview = document.getElementById('image-preview');
      if (!preview) return;
      preview.innerHTML = '';
      Array.from(this.files).slice(0, 5).forEach(function (file) {
        var reader = new FileReader();
        reader.onload = function (ev) {
          var img = document.createElement('img');
          img.src = ev.target.result;
          img.style.cssText = 'width:80px;height:80px;object-fit:cover;margin:4px;border-radius:4px;border:1px solid #ccc;';
          preview.appendChild(img);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  /* ── Auto-dismiss alerts after 5s ── */
  setTimeout(function () {
    var alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(function (a) {
      if (typeof jQuery !== 'undefined') {
        jQuery(a).fadeOut(600, function () { this.remove(); });
      } else {
        a.style.display = 'none';
      }
    });
  }, 5000);

  /* ── Payment method toggle ── */
  var payMethodRadios = document.querySelectorAll('input[name="payment_method"]');
  payMethodRadios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      var paystackInfo = document.getElementById('paystack-info');
      var podInfo = document.getElementById('pod-info');
      if (!paystackInfo || !podInfo) return;
      if (this.value === 'paystack') {
        paystackInfo.style.display = 'block';
        podInfo.style.display = 'none';
      } else {
        paystackInfo.style.display = 'none';
        podInfo.style.display = 'block';
      }
    });
  });

})();
