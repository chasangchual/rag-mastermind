(function () {
  const root = document.documentElement;
  const body = document.body;

  const select = document.getElementById('themeSelect');
  const savedTheme = localStorage.getItem('kgcs-theme') || 'theme-blue-green';

  root.setAttribute('data-theme', savedTheme);

  if (select) {
    select.value = savedTheme;
  }

  select?.addEventListener('change', function () {
    root.setAttribute('data-theme', this.value);
    localStorage.setItem('kgcs-theme', this.value);
  });

  const chatInput = document.getElementById('chatInput');
  const sendButton = document.getElementById('sendChat');
  const chatMessages = document.getElementById('chatMessages');
  const wsStatus = document.getElementById('wsStatus');
  const traceList = document.getElementById('traceList');
  const traceLatency = document.getElementById('traceLatency');
  const traceMode = document.getElementById('traceMode');

  const sessionId = body?.dataset?.sessionId || '';
  const currentPage = body?.dataset?.page || '';

  let socket = null;
  let isSocketReady = false;
  let pendingStartedAt = null;

  function setStatus(label, statusClass) {
    if (!wsStatus) {
      return;
    }

    wsStatus.className = `badge rounded-pill ${statusClass}`;
    wsStatus.textContent = label;
  }

  function appendMessage(role, text, options = {}) {
    if (!chatMessages || !String(text || '').trim()) {
      return;
    }

    const wrap = document.createElement('div');
    wrap.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = role === 'user' ? 'You' : 'Assistant';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    if (options.citations && options.citations.length > 0) {
      const citationRow = document.createElement('div');
      citationRow.className = 'citation-row';

      options.citations.forEach((citation) => {
        const chip = document.createElement('span');
        chip.className = 'citation-chip';
        chip.textContent = citation;
        citationRow.appendChild(chip);
      });

      bubble.appendChild(citationRow);
    }

    wrap.appendChild(label);
    wrap.appendChild(bubble);

    chatMessages.appendChild(wrap);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function updateTrace(meta) {
    if (!meta) {
      return;
    }

    const retrieval = meta.retrieval || {};

    if (traceMode) {
      traceMode.textContent = retrieval.mode || 'WS';
    }

    if (pendingStartedAt && traceLatency) {
      traceLatency.textContent = `${Date.now() - pendingStartedAt} ms`;
    }

    if (!traceList) {
      return;
    }

    const chunks = retrieval.chunks || [];

    if (chunks.length === 0) {
      return;
    }

    traceList.innerHTML = '';

    chunks.forEach((chunk) => {
      const item = document.createElement('div');
      item.className = 'trace-item';

      item.innerHTML = `
        <strong></strong>
        <span></span>
        <p></p>
      `;

      item.querySelector('strong').textContent = chunk.id || 'chunk';
      item.querySelector('span').textContent = `score ${chunk.score ?? '--'}`;
      item.querySelector('p').textContent =
        chunk.preview || chunk.source || 'Retrieved chunk preview.';

      traceList.appendChild(item);
    });
  }

  function websocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/app/ws`;
  }

  function connectWebSocket() {
    if (currentPage !== 'chat' || !chatMessages) {
      return;
    }

    setStatus('Connecting', 'text-bg-warning-soft');

    socket = new WebSocket(websocketUrl());

    socket.addEventListener('open', function () {
      socket.send(JSON.stringify({
        type: 'cw_chat_hello',
        session_id: sessionId,
      }));
    });

    socket.addEventListener('message', function (event) {
      let payload;

      try {
        payload = JSON.parse(event.data);
      } catch (error) {
        appendMessage('assistant', 'Received a non-JSON WebSocket message from the server.');
        return;
      }

      switch (payload.type) {
        case 'connection_ready':
          isSocketReady = true;
          setStatus('WebSocket Ready', 'text-bg-success-soft');
          break;

        case 'ack':
          break;

        case 'typing':
          setStatus(
            payload.state ? 'Assistant typing' : 'WebSocket Ready',
            payload.state ? 'text-bg-info-soft' : 'text-bg-success-soft',
          );
          break;

        case 'assistant_message': {
          const message = payload.message || {};

          const citations =
            message?.meta?.retrieval?.chunks?.map(
              (chunk) => `${chunk.source || 'source'} · ${chunk.id || 'chunk'}`,
            ) || [];

          appendMessage('assistant', message.content || 'No response content.', {
            citations,
          });

          updateTrace(message.meta);
          pendingStartedAt = null;
          break;
        }

        case 'error':
          setStatus('WebSocket Error', 'text-bg-danger-soft');
          appendMessage('assistant', payload.error || 'Unknown WebSocket error.');
          pendingStartedAt = null;
          break;

        case 'pong':
          break;

        default:
          appendMessage('assistant', `Unhandled WebSocket event: ${payload.type}`);
      }
    });

    socket.addEventListener('close', function () {
      isSocketReady = false;
      setStatus('Disconnected', 'text-bg-danger-soft');
    });

    socket.addEventListener('error', function () {
      isSocketReady = false;
      setStatus('WebSocket Error', 'text-bg-danger-soft');
    });
  }

  function sendChatMessage() {
    const value = (chatInput?.value || '').trim();

    if (!value) {
      return;
    }

    appendMessage('user', value);
    chatInput.value = '';

    if (!socket || socket.readyState !== WebSocket.OPEN || !isSocketReady) {
      appendMessage(
        'assistant',
        'WebSocket is not connected yet. Please refresh or try again in a moment.',
      );
      return;
    }

    pendingStartedAt = Date.now();

    socket.send(JSON.stringify({
      type: 'user_message',
      text: value,
    }));
  }

  sendButton?.addEventListener('click', sendChatMessage);

  chatInput?.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      sendChatMessage();
    }
  });

  connectWebSocket();
})();