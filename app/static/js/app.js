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
  const documentsCount = document.getElementById('documentsCount');
  const documentsTableBody = document.getElementById('documentsTableBody');
  const chooseFilesButton = document.getElementById('chooseFilesButton');
  const documentFileInput = document.getElementById('documentFileInput');
  const documentUploadStatus = document.getElementById('documentUploadStatus');

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
    return `${protocol}//${window.location.host}/app/chat/ws`;
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

  function formatDocumentCount(count) {
    return `${count.toLocaleString()} ${count === 1 ? 'document' : 'documents'}`;
  }

  function statusClass(state) {
    const normalizedState = String(state || '').toLowerCase();

    if (['ready', 'complete', 'completed', 'embedded', 'processed'].includes(normalizedState)) {
      return 'text-bg-success-soft';
    }

    if (['failed', 'error'].includes(normalizedState)) {
      return 'text-bg-danger-soft';
    }

    if (['pending', 'parsing', 'processing', 'ingesting'].includes(normalizedState)) {
      return 'text-bg-warning-soft';
    }

    return 'text-bg-info-soft';
  }

  function shortValue(value, maxLength = 16) {
    const text = String(value || '').trim();

    if (!text) {
      return '--';
    }

    return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
  }

  function sourceLabel(documentEntity) {
    return documentEntity.source || documentEntity.meta?.filename || documentEntity.meta?.name || 'Untitled document';
  }

  function renderDocuments(documents) {
    if (!documentsTableBody) {
      return;
    }

    documentsTableBody.innerHTML = '';

    if (documentsCount) {
      documentsCount.textContent = formatDocumentCount(documents.length);
    }

    if (documents.length === 0) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 5;
      cell.className = 'text-center text-muted py-4';
      cell.textContent = 'No documents found.';
      row.appendChild(cell);
      documentsTableBody.appendChild(row);
      return;
    }

    documents.forEach((documentEntity) => {
      const row = document.createElement('tr');
      const sourceCell = document.createElement('td');
      const statusCell = document.createElement('td');
      const extensionCell = document.createElement('td');
      const hashCell = document.createElement('td');
      const idCell = document.createElement('td');
      const statusBadge = document.createElement('span');

      sourceCell.textContent = sourceLabel(documentEntity);
      statusBadge.className = `badge ${statusClass(documentEntity.state)}`;
      statusBadge.textContent = documentEntity.state || 'unknown';
      statusCell.appendChild(statusBadge);
      extensionCell.textContent = documentEntity.extension || '--';
      hashCell.textContent = shortValue(documentEntity.hash);
      hashCell.title = documentEntity.hash || '';
      idCell.textContent = shortValue(documentEntity.public_id, 18);
      idCell.title = documentEntity.public_id || '';

      row.appendChild(sourceCell);
      row.appendChild(statusCell);
      row.appendChild(extensionCell);
      row.appendChild(hashCell);
      row.appendChild(idCell);
      documentsTableBody.appendChild(row);
    });
  }

  function renderDocumentsError() {
    if (documentsCount) {
      documentsCount.textContent = 'Unavailable';
    }

    if (!documentsTableBody) {
      return;
    }

    documentsTableBody.innerHTML = '';

    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.className = 'text-center text-muted py-4';
    cell.textContent = 'Unable to load documents.';
    row.appendChild(cell);
    documentsTableBody.appendChild(row);
  }

  function setDocumentUploadStatus(message, className = 'small text-muted mt-3') {
    if (!documentUploadStatus) {
      return;
    }

    documentUploadStatus.className = className;
    documentUploadStatus.textContent = message;
  }

  async function loadDocuments() {
    if (currentPage !== 'documents' || !documentsTableBody) {
      return;
    }

    try {
      const response = await fetch('/app/api/documents', {
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Documents request failed with ${response.status}`);
      }

      const documents = await response.json();
      renderDocuments(Array.isArray(documents) ? documents : []);
    } catch (error) {
      renderDocumentsError();
    }
  }

  async function uploadDocuments(files) {
    if (!files || files.length === 0) {
      return;
    }

    const formData = new FormData();
    const fileCount = files.length;

    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    if (chooseFilesButton) {
      chooseFilesButton.disabled = true;
    }
    setDocumentUploadStatus(
      `Uploading ${fileCount.toLocaleString()} ${fileCount === 1 ? 'file' : 'files'}...`,
    );

    try {
      const response = await fetch('/app/api/documents/upload', {
        method: 'POST',
        body: formData,
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Upload request failed with ${response.status}`);
      }

      await response.json();
      setDocumentUploadStatus(
        `Uploaded ${fileCount.toLocaleString()} ${fileCount === 1 ? 'file' : 'files'}.`,
        'small text-success mt-3',
      );
      await loadDocuments();
    } catch (error) {
      setDocumentUploadStatus('Unable to upload selected files.', 'small text-danger mt-3');
    } finally {
      if (chooseFilesButton) {
        chooseFilesButton.disabled = false;
      }

      if (documentFileInput) {
        documentFileInput.value = '';
      }
    }
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

  chooseFilesButton?.addEventListener('click', function () {
    documentFileInput?.click();
  });

  documentFileInput?.addEventListener('change', function () {
    uploadDocuments(this.files);
  });

  connectWebSocket();
  loadDocuments();
})();
