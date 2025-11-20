document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  const remember = document.getElementById('remember');
  const toggle = document.getElementById('toggle-password');
  const msg = document.getElementById('form-message');
  const submitBtn = document.getElementById('submit-btn');

  // Prefill username if remembered
  try {
    const stored = localStorage.getItem('login.username');
    if (stored) { email.value = stored; remember.checked = true; }
  } catch (e) {}

  // Toggle password visibility
  toggle.addEventListener('click', () => {
    const t = password.type === 'password' ? 'text' : 'password';
    password.type = t;
    toggle.textContent = t === 'password' ? 'Show' : 'Hide';
    toggle.setAttribute('aria-label', t === 'password' ? 'Show password' : 'Hide password');
  });

  function setError(el, text) {
    el.classList.add('invalid');
    msg.textContent = text;
    msg.style.color = '#e55353';
  }

  function clearError() {
    email.classList.remove('invalid');
    password.classList.remove('invalid');
    msg.textContent = '';
    msg.style.color = '';
  }

  function validate() {
    clearError();
    if (!email.value || !email.value.trim()) { setError(email, 'Please enter your email or username'); return false; }
    if (!password.value || password.value.length < 6) { setError(password, 'Password must be at least 6 characters'); return false; }
    return true;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!validate()) return;

    submitBtn.disabled = true;
    const orig = submitBtn.textContent;
    submitBtn.textContent = 'Signing in…';
    msg.textContent = '';

    // POST to backend /login (expects JSON response { success, message, redirect })
    fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })
    .then(async res => {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const message = data && data.message ? data.message : 'Login failed';
        throw new Error(message);
      }
      return data;
    })
    .then(data => {
      submitBtn.disabled = false;
      submitBtn.textContent = orig;
      msg.style.color = 'green';
      msg.textContent = data.message || 'Signed in';

      // remember username if requested
      try {
        if (remember.checked) localStorage.setItem('login.username', email.value);
        else localStorage.removeItem('login.username');
      } catch (e) {}

      // redirect if server specified a redirect
      if (data.redirect) {
        window.location.href = data.redirect;
      }
    })
    .catch(err => {
      submitBtn.disabled = false;
      submitBtn.textContent = orig;
      msg.style.color = '#e55353';
      msg.textContent = err.message || 'Sign in failed';
    });
  });

  // clear errors when user types
  [email, password].forEach(el => {
    el.addEventListener('input', () => {
      el.classList.remove('invalid');
      msg.textContent = '';
    });
  });
});
