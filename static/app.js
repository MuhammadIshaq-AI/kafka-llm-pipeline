document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-upload');
    const statusMsg = document.getElementById('upload-status');
    const chatForm = document.getElementById('chat-form');
    const queryInput = document.getElementById('query-input');
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const refreshBtn = document.getElementById('refresh-chat-btn');

    // Refresh Context Action
    refreshBtn.addEventListener('click', () => {
        chatBox.innerHTML = `
            <div class="message ai-message">
                <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="content">Context refreshed! What would you like to ask?</div>
            </div>
        `;
    });

    // API Base URL (Relative for FastAPI)
    const API_BASE = '/api';

    // File Upload Handlers
    const handleFiles = async (files) => {
        if (files.length === 0) return;
        const file = files[0];

        if (file.type !== 'application/pdf') {
            showStatus('Please upload a PDF file.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        showStatus(`Uploading ${file.name}... <i class="fa-solid fa-spinner fa-spin"></i>`, 'loading');

        try {
            const res = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();

            if (res.ok) {
                showStatus(`<i class="fa-solid fa-check"></i> ${file.name} uploaded to S3. Processing embeddings...`, 'success');
            } else {
                throw new Error(data.detail || 'Upload failed');
            }
        } catch (error) {
            showStatus(`<i class="fa-solid fa-triangle-exclamation"></i> ${error.message}`, 'error');
        }
    };

    const showStatus = (msg, type) => {
        statusMsg.innerHTML = msg;
        statusMsg.className = `status-msg ${type}`;
    };

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    // Chat Handlers
    const addMessage = (html, isUser = false) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

        const avatar = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="content">${html}</div>
        `;

        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return msgDiv;
    };

    const addLoader = () => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ai-message loader';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return msgDiv;
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        // UI Updates
        addMessage(query, true);
        queryInput.value = '';
        sendBtn.disabled = true;
        const loader = addLoader();

        try {
            const res = await fetch(`${API_BASE}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await res.json();
            loader.remove();

            if (res.ok) {
                let html = `<p>${data.response}</p>`;
                if (data.context_used && data.context_used.length > 0) {
                    html += `<div class="context-used">
                        <strong><i class="fa-solid fa-layer-group"></i> Context Used:</strong>
                        <div class="context-item">${data.context_used[0].substring(0, 150)}...</div>
                    </div>`;
                }
                addMessage(html);
            } else {
                throw new Error(data.detail || 'Query failed');
            }
        } catch (error) {
            loader.remove();
            addMessage(`<span style="color: var(--error);"><i class="fa-solid fa-triangle-exclamation"></i> Error: ${error.message}</span>`);
        } finally {
            sendBtn.disabled = false;
            queryInput.focus();
        }
    });
});
