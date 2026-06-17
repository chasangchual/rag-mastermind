(function () {
  const root = document.documentElement;
  const select = document.getElementById('themeSelect');
  const savedTheme = localStorage.getItem('kgcs-theme') || 'theme-blue-green';
  root.setAttribute('data-theme', savedTheme);
  if (select) select.value = savedTheme;

  select?.addEventListener('change', function () {
    root.setAttribute('data-theme', this.value);
    localStorage.setItem('kgcs-theme', this.value);
  });

  const chatInput = document.getElementById('chatInput');
  const sendButton = document.getElementById('sendChat');
  const chatMessages = document.getElementById('chatMessages');

  function appendMessage(role, text) {
    if (!chatMessages || !text.trim()) return;
    const wrap = document.createElement('div');
    wrap.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;
    wrap.innerHTML = `<div class="message-label">${role === 'user' ? 'You' : 'Assistant'}</div><div class="message-bubble"></div>`;
    wrap.querySelector('.message-bubble').textContent = text;
    chatMessages.appendChild(wrap);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  sendButton?.addEventListener('click', function () {
    const value = chatInput.value;
    appendMessage('user', value);
    chatInput.value = '';
    setTimeout(() => appendMessage('assistant', 'Mock response: this would call your FastAPI RAG endpoint, retrieve chunks, and return a cited answer.'), 250);
  });

  chatInput?.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') sendButton?.click();
  });
})();
