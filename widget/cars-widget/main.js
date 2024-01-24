import {CLOSE_ICON, MESSAGE_ICON, styles} from "./assets.js";

class MessageWidget {
    constructor(position = "bottom-right") {
        this.position = this.getPosition(position);
        this.open = false;
        this.initialize();
        this.injectStyles();
    }

    position = "";
    open = false;
    widgetContainer = null;
    chatBox = null;
    messagesHistory = [];
    identifierToken = '';
    url = 'http://127.0.0.1:8080/api/chat';

    getPosition(position) {
        const [vertical, horizontal] = position.split("-");
        return {
            [vertical]: "30px",
            [horizontal]: "30px",
        };
    }

    async initialize() {
        /**
         * Create and append a div element to the document body
         */
        const container = document.createElement("div");
        container.style.position = "fixed";
        Object.keys(this.position).forEach(
            (key) => (container.style[key] = this.position[key])
        );
        document.body.appendChild(container);

        /**
         * Create a button element and give it a class of button__container
         */
        const buttonContainer = document.createElement("button");
        buttonContainer.classList.add("button__container");

        /**
         * Create a span element for the widget icon, give it a class of `widget__icon`, and update its innerHTML property to an icon that would serve as the widget icon.
         */
        const widgetIconElement = document.createElement("span");
        widgetIconElement.innerHTML = MESSAGE_ICON;
        widgetIconElement.classList.add("widget__icon");
        this.widgetIcon = widgetIconElement;

        /**
         * Create a span element for the close icon, give it a class of `widget__icon` and `widget__hidden` which would be removed whenever the widget is closed, and update its innerHTML property to an icon that would serve as the widget icon during that state.
         */
        const closeIconElement = document.createElement("span");
        closeIconElement.innerHTML = CLOSE_ICON;
        closeIconElement.classList.add("widget__icon", "widget__hidden");
        this.closeIcon = closeIconElement;

        /**
         * Append both icons created to the button element and add a `click` event listener on the button to toggle the widget open and close.
         */
        buttonContainer.appendChild(this.widgetIcon);
        buttonContainer.appendChild(this.closeIcon);

        /**
         * Create a container for the widget and add the following classes:- `widget__hidden`, `widget__container`
         */
        this.widgetContainer = document.createElement("div");
        this.widgetContainer.classList.add("widget__hidden", "widget__container");

        /**
         * Invoke the `createWidget()` method
         */
        this.createWidgetContent();

        /**
         * Append the widget's content and the button to the container
         */
        container.appendChild(this.widgetContainer);
        container.appendChild(buttonContainer);

        buttonContainer.addEventListener("click", this.toggleOpen.bind(this));

        this.chatBox = document.getElementById('widget__messages_box');

        this.scrollToBottom();
    }

    createWidgetContent() {
        this.widgetContainer.innerHTML = `
        <header class="widget__header">
            <h3>Chat with our AI Helper</h3>
            <p>He will try to help you pick a car you want</p>
        </header>
        
        <div class="widget__messages_box" id="widget__messages_box">
            <div class="container">
                <span>AI</span>
                <p>Hello, how can I help you?</p>
            </div>
        </div>
        
        <form>
            <div class="form__field">
                <label for="widget__message">Message</label>
                <textarea
                  id="widget__message"
                  name="message"
                  placeholder="Enter your message"
                  rows="6"
                ></textarea>
            </div>
            <button onclick="return chatWidget.sendMessage();">Send Message</button>
        </form>
    `;
    }

    injectStyles() {
        const styleTag = document.createElement("style");
        styleTag.innerHTML = styles.replace(/^\s+|\n/gm, "");
        document.head.appendChild(styleTag);
    }

    toggleOpen() {
        this.open = !this.open;
        if (this.open) {
            this.widgetIcon.classList.add("widget__hidden");
            this.closeIcon.classList.remove("widget__hidden");
            this.widgetContainer.classList.remove("widget__hidden");
            this.scrollToBottom();
        } else {
            this.widgetIcon.classList.remove("widget__hidden");
            this.closeIcon.classList.add("widget__hidden");
            this.widgetContainer.classList.add("widget__hidden");
        }
    }

    messageTemplate() {
        return '<div class="container">\n<span>##USER##</span>\n<p>##MESSAGE##</p>\n</div>';
    }

    retrieveIdentifier() {
        // You can retrieve the identifier from the localStorage and use it for chat history if needed
        // We have skipped this part. Each reload is new session
        this.identifierToken = Date.now().toString(36) + Math.random().toString(36).substring(2);
        localStorage.setItem('widget__identifier', this.identifierToken);

        return this.identifierToken;
    }

    addMessage(message, sender) {
        this.messagesHistory.push({
            message,
            sender,
        });
        let messageTemplate = this.messageTemplate();
        messageTemplate = messageTemplate.replace('##USER##', sender);
        messageTemplate = messageTemplate.replace('##MESSAGE##', message);
        this.chatBox.innerHTML += messageTemplate;
    }

    sendMessage() {
        // Get the message
        let messageBox = document.getElementById('widget__message');
        let message = messageBox.value;

        // Save the message to messages list
        this.addMessage(message, 'You');

        // Send GPT prompt to the server
        this.requestResponse(message)
            .then((resp) => {
                console.log(resp.data.answer)
                // Add the message to the chat box
                this.addMessage(resp.data.answer, 'AI');

                // Reset the message box value to '' (empty)
                messageBox.value = '';

                // Scroll the chatbox automatically
                this.scrollToBottom();
            });

        // Prevent form submission
        return false;
    }

    async requestResponse(message) {
        const resp = await fetch(this.url, {
            method: "POST",
            body: JSON.stringify({
                "query": message,
                "identifier": this.retrieveIdentifier()
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        });

        const data = await resp.json();

        if (data.data.answer == null) {
            return this.requestResponse(message)
        } else if (data.data.answer) {
            return data;
        }
    }

    scrollToBottom() {
        this.chatBox.scrollTop = this.chatBox.scrollHeight;
    }
}

function initializeWidget() {
    return new MessageWidget();
}

window.chatWidget = initializeWidget();