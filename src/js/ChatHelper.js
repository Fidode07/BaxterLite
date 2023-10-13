class Message {
    constructor(message, sender) {
        this.message = message;
        this.sender = sender;
    }

    getHtml() {
        return `<div class="message ${this.sender}">
                    <div class="text">
                        <p>${this.message}</p>
                    </div> 
                </div>`;
    }
}

function pushMessage(message, sender) {
    const messageObject = new Message(message, sender);
    const messageContainer = document.getElementById('message-container');

    messageContainer.innerHTML += messageObject.getHtml();
}

function setUiDisabled(disabled) {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-btn');

    messageInput.disabled = disabled;
    sendButton.disabled = disabled;
}

function handleMessage(inputMessage) {
    // disable button and input field
    setUiDisabled(true);
    // Send message to backend
    pywebview.api.get_response(inputMessage).then(function (response) {
        // enable button and input field
        pushMessage(response.response, 'ai');
        // enable button and input field
        setUiDisabled(false);

        // scroll to bottom
        const messageContainer = document.getElementById('message-container');
        messageContainer.scrollTop = messageContainer.scrollHeight;
    });
}


function sendMessage() {
    const messageContainer = document.getElementById('message-container');
    const messageField = document.getElementById('message-input');
    let message = messageField.value;
    if (!message) return;
    pushMessage(message, 'user');
    messageField.value = '';
    messageContainer.scrollTop = messageContainer.scrollHeight;

    handleMessage(message);
}

document.addEventListener('keyup', function (event) {
    if (event.code !== 'Enter') {
        // focus input field
        document.getElementById('message-input').focus();
        return;
    }
    sendMessage();
});

// hold document scroll position always at bottom
document.addEventListener('DOMContentLoaded', function () {
    const messageContainer = document.getElementById('message-container');
    messageContainer.scrollTop = messageContainer.scrollHeight;
});