document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const username = document.getElementById('username');
  const email = document.getElementById('email');
  const nameInput = document.getElementById('name');
  const password = document.getElementById('password');
  const confirm = document.getElementById('confirm');
  const msg = document.getElementById('form-message');
  const submitBtn = document.getElementById('submit-btn');

  function setError(text) {
    msg.style.color = '#e55353';
    msg.textContent = text;
  }

  function clearError() {
    msg.textContent = '';
    msg.style.color = '';
  }

  function validate() {
    clearError();
    if (!username.value && !email.value) { setError('Please provide a username or email'); return false; }
    if (!password.value || password.value.length < 6) { setError('Password must be at least 6 characters'); return false; }
    if (password.value !== confirm.value) { setError('Passwords do not match'); return false; }
    return true;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!validate()) return;

    submitBtn.disabled = true;
    const orig = submitBtn.textContent;
    submitBtn.textContent = 'Creating…';

    fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        name: nameInput.value,
        password: password.value
      })
    })
    .then(async res => {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.message || 'Registration failed');
      return data;
    })
    .then(data => {
      submitBtn.disabled = false;
      submitBtn.textContent = orig;
      msg.style.color = 'green';
      msg.textContent = data.message || 'Registered';
      if (data.redirect) window.location.href = data.redirect;
    })
    .catch(err => {
      submitBtn.disabled = false;
      submitBtn.textContent = orig;
      setError(err.message || 'Registration failed');
    });
  });
});
