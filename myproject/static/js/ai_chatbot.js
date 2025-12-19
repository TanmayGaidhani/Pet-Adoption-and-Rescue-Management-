// ===== AI CHATBOT WITH GOOGLE GEMINI =====

class AIChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createChatbotHTML();
        this.attachEventListeners();
    }

    createChatbotHTML() {
        const chatbotHTML = `
            <!-- Floating Chat Button -->
            <button class="ai-chat-button" id="aiChatButton" aria-label="Open chat">
                <img src="/static/images/chatboticon.png" alt="Chat" class="chat-button-icon">
            </button>

            <!-- Chat Window -->
            <div class="ai-chat-window" id="aiChatWindow">
                <!-- Header -->
                <div class="ai-chat-header">
                    <div class="chat-header-content">
                        <div class="chat-bot-avatar">
                            <img src="/static/images/chatboticon.png" alt="Bot" style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                        <div class="chat-bot-info">
                            <h3>PetCare AI</h3>
                            <div class="chat-bot-status">
                                <span class="status-dot"></span>
                                <span>Online & Ready</span>
                            </div>
                        </div>
                    </div>
                    <button class="chat-close-btn" id="chatCloseBtn" aria-label="Close chat">
                        ×
                    </button>
                </div>

                <!-- Messages Area -->
                <div class="ai-chat-messages" id="aiChatMessages">
                    <div class="chat-welcome">
                        <img src="/static/images/chatboticon.png" alt="PetCare AI" class="welcome-icon" style="width: 64px; height: 64px; object-fit: contain;">
                        <h3>Hello! I'm PetCare AI</h3>
                        <p>Your intelligent assistant for all animal-related questions. Ask me about pet care, health, training, nutrition, and more!</p>
                        
                        <div class="quick-actions">
                            <button class="quick-action-btn" onclick="aiChatbot.sendQuickMessage('How do I care for a new puppy?')">
                                <span class="quick-action-icon">🐕</span>
                                <span class="quick-action-text">Puppy Care</span>
                            </button>
                            <button class="quick-action-btn" onclick="aiChatbot.sendQuickMessage('What should I feed my cat?')">
                                <span class="quick-action-icon">🐱</span>
                                <span class="quick-action-text">Cat Nutrition</span>
                            </button>
                            <button class="quick-action-btn" onclick="aiChatbot.sendQuickMessage('How to train my dog?')">
                                <span class="quick-action-icon">🎓</span>
                                <span class="quick-action-text">Dog Training</span>
                            </button>
                            <button class="quick-action-btn" onclick="aiChatbot.sendQuickMessage('Signs of pet illness?')">
                                <span class="quick-action-icon">🏥</span>
                                <span class="quick-action-text">Pet Health</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="ai-chat-input-area">
                    <div class="chat-input-wrapper">
                        <textarea 
                            class="ai-chat-input" 
                            id="aiChatInput" 
                            placeholder="Ask me anything about animals..."
                            rows="1"
                        ></textarea>
                        <button class="chat-send-btn" id="chatSendBtn" aria-label="Send message">
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    attachEventListeners() {
        const chatButton = document.getElementById('aiChatButton');
        const closeBtn = document.getElementById('chatCloseBtn');
        const sendBtn = document.getElementById('chatSendBtn');
        const input = document.getElementById('aiChatInput');

        chatButton.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        sendBtn.addEventListener('click', () => this.sendMessage());

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        input.addEventListener('input', () => this.autoResizeInput(input));
    }

    toggleChat() {
        const chatWindow = document.getElementById('aiChatWindow');
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chatWindow.classList.add('active');
            document.getElementById('aiChatInput').focus();
        } else {
            chatWindow.classList.remove('active');
        }
    }

    closeChat() {
        const chatWindow = document.getElementById('aiChatWindow');
        chatWindow.classList.remove('active');
        this.isOpen = false;
    }

    autoResizeInput(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    sendQuickMessage(message) {
        document.getElementById('aiChatInput').value = message;
        this.sendMessage();
    }

    async sendMessage() {
        const input = document.getElementById('aiChatInput');
        const message = input.value.trim();

        if (!message || this.isTyping) return;

        // Clear input
        input.value = '';
        this.autoResizeInput(input);

        // Add user message
        this.addMessage(message, 'user');

        // Check if question seems pet-related (basic filter)
        if (!this.isPetRelated(message)) {
            setTimeout(() => {
                this.addMessage(
                    "I'm sorry, but I can only answer questions related to pets and animals. 🐾 Please ask me about pet care, animal health, training, nutrition, or any animal-related topics!",
                    'bot'
                );
            }, 500);
            return;
        }

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend API
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    history: this.messages.slice(-10) // Send last 10 messages for context
                })
            });

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }

        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'bot');
        }
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('aiChatMessages');
        
        // Remove welcome screen if exists
        const welcomeScreen = messagesContainer.querySelector('.chat-welcome');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const avatar = sender === 'bot' 
            ? '<img src="/static/images/chatboticon.png" alt="Bot" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">' 
            : '👤';
        const time = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageDiv.innerHTML = `
            <div class="message-avatar ${sender}">${avatar}</div>
            <div class="message-content">
                <div class="message-bubble">${this.formatMessage(text)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message in history
        this.messages.push({ text, sender, time });
    }

    formatMessage(text) {
        // Convert markdown-style formatting to HTML
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/\n/g, '<br>');
        return text;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('aiChatMessages');
        this.isTyping = true;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar bot">
                <img src="/static/images/chatboticon.png" alt="Bot" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
            </div>
            <div class="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('aiChatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    isPetRelated(message) {
        const lowerMessage = message.toLowerCase();
        
        // Pet/animal related keywords
        const petKeywords = [
            'dog', 'cat', 'pet', 'animal', 'puppy', 'kitten', 'bird', 'fish', 'rabbit',
            'hamster', 'guinea pig', 'parrot', 'turtle', 'lizard', 'snake', 'horse',
            'vet', 'veterinary', 'paw', 'tail', 'fur', 'feather', 'breed', 'adoption',
            'rescue', 'shelter', 'feed', 'food', 'train', 'bark', 'meow', 'cage',
            'leash', 'collar', 'groom', 'vaccine', 'flea', 'tick', 'wildlife',
            'mammal', 'reptile', 'amphibian', 'canine', 'feline', 'rodent'
        ];
        
        // Check if message contains any pet-related keywords
        const hasPetKeyword = petKeywords.some(keyword => lowerMessage.includes(keyword));
        
        // If message is very short (like "hi", "hello"), allow it
        if (message.length < 15 && (
            lowerMessage.includes('hi') || 
            lowerMessage.includes('hello') || 
            lowerMessage.includes('hey') ||
            lowerMessage.includes('help')
        )) {
            return true;
        }
        
        return hasPetKeyword;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize chatbot when DOM is ready
let aiChatbot;
document.addEventListener('DOMContentLoaded', function() {
    aiChatbot = new AIChatbot();
});
