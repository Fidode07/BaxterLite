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

function scrollDown() {
    const messageContainer = document.getElementById('message-container');
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function pushMessage(message, sender) {
    const messageObject = new Message(message, sender);
    const messageContainer = document.getElementById('message-container');

    messageContainer.innerHTML += messageObject.getHtml();
    scrollDown();
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
        if (!response.response) {
            setUiDisabled(false);
            return; // happens when action is not returning a response
        }
        pushMessage(response.response, 'ai');
        // enable button and input field
        setUiDisabled(false);

        // scroll to bottom
        scrollDown();
    });
}

function clear_chat() {
    const messageContainer = document.getElementById('message-container');
    let children = messageContainer.children;
    // remove all children except the first one
    for (let i = children.length - 1; i > 0; i--) {
        messageContainer.removeChild(children[i]);
    }
}

let isPromptWaiting = false;

function sendMessage() {
    const messageField = document.getElementById('message-input');
    let message = messageField.value;
    if (!message) return;
    pushMessage(message, 'user');
    messageField.value = '';
    // scroll to bottom
    scrollDown();

    if (!isPromptWaiting) {
        handleMessage(message);
        return;
    }
    // User answered a prompt
    isPromptWaiting = false;
    pywebview.api.prompt_response(message);
}

function set_prompt(message) {
    pushMessage(message, 'ai');
    isPromptWaiting = true;

    // Enable input because user has to answer prompt
    setUiDisabled(false);

    // focus input field and scroll to bottom
    scrollDown();
    document.getElementById('message-input').focus();
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
    scrollDown();
});