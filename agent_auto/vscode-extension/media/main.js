// main.js
(function() {
    const vscode = acquireVsCodeApi();

    const chatLog = document.getElementById('chat-log');
    const userInput = document.getElementById('user-input');

    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            const message = userInput.value;
            userInput.value = '';

            addMessage('user', message);
            vscode.postMessage({
                command: 'sendMessage',
                text: message
            });
        }
    });

    window.addEventListener('message', event => {
        const message = event.data;
        switch (message.command) {
            case 'addMessage':
                addMessage(message.type, message.text);
                break;
        }
    });

    function addMessage(type, text) {
        const li = document.createElement('li');
        li.className = type;
        li.textContent = text;
        chatLog.appendChild(li);
    }
}());
