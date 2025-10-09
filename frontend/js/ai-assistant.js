class AIAssistant {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.addMessage("Hello! I'm your MediCart assistant. How can I help you today?", 'bot');
    }

    setupEventListeners() {
        const chatToggle = document.getElementById('chatToggle');
        const chatWindow = document.getElementById('chatWindow');
        const closeChat = document.getElementById('closeChat');
        const sendMessage = document.getElementById('sendMessage');
        const chatInput = document.getElementById('chatInput');

        if (chatToggle) chatToggle.addEventListener('click', () => this.toggleChat());
        if (closeChat) closeChat.addEventListener('click', () => this.closeChat());
        if (sendMessage) sendMessage.addEventListener('click', () => this.handleSendMessage());
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSendMessage();
                }
            });
        }
    }

    toggleChat() {
        const chatWindow = document.getElementById('chatWindow');
        this.isOpen = !this.isOpen;
        if (chatWindow) {
            chatWindow.style.display = this.isOpen ? 'flex' : 'none';
        }
    }

    closeChat() {
        const chatWindow = document.getElementById('chatWindow');
        this.isOpen = false;
        if (chatWindow) {
            chatWindow.style.display = 'none';
        }
    }

    async handleSendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput ? chatInput.value.trim() : '';
        
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        if (chatInput) chatInput.value = '';

        // Show loading indicator
        const loadingId = this.addMessage('Thinking...', 'bot', true);

        try {
            const response = await this.getAIResponse(message);
            this.updateMessage(loadingId, response, 'bot');
        } catch (error) {
            this.updateMessage(loadingId, "I'm sorry, I'm having trouble connecting right now. Please try again later.", 'bot');
        }
    }

    async getAIResponse(message) {
        try {
            const response = await fetch(`${API_BASE_URL}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: this.getContext()
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get AI response');
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('AI Response Error:', error);
            return this.getFallbackResponse(message);
        }
    }

    getContext() {
        return {
            website: 'MediCart Pharmacy',
            services: [
                'Medicine Request',
                'Prescription Upload',
                'Pharmacist Consultation',
                'Medical Equipment Rental',
                'Supplement Recommendations',
                'Health Tips and Resources',
                'Emergency Services'
            ],
            currentPage: window.location.pathname.split('/').pop() || 'index.html'
        };
    }

    getFallbackResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('medicine') || lowerMessage.includes('prescription')) {
            return "You can request medicines or upload prescriptions through our services. Would you like me to direct you to the appropriate page?";
        } else if (lowerMessage.includes('emergency') || lowerMessage.includes('urgent')) {
            return "For emergency requests, please use our emergency services page. We prioritize urgent medication needs.";
        } else if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
            return "Product prices vary. You can check our products page for detailed pricing information.";
        } else if (lowerMessage.includes('delivery') || lowerMessage.includes('shipping')) {
            return "We offer delivery services for all orders. Standard delivery takes 2-3 business days, with express options available.";
        } else if (lowerMessage.includes('hours') || lowerMessage.includes('open')) {
            return "Our opening hours are Monday-Friday 8:00-17:00, Saturday 9:30-17:30, and Sunday 8:30-16:00.";
        } else if (lowerMessage.includes('contact') || lowerMessage.includes('phone')) {
            return "You can contact us at support@medicart.com or call +880-XXXX-XXXX during business hours.";
        } else {
            return "I'm here to help with MediCart services. You can ask about medicines, prescriptions, consultations, or our other services.";
        }
    }

    addMessage(text, sender, isTemp = false) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return null;
        
        const messageId = isTemp ? 'temp-' + Date.now() : null;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        
        if (messageId) {
            messageDiv.id = messageId;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        if (!isTemp) {
            this.messages.push({ text, sender });
        }
        
        return messageId;
    }

    updateMessage(messageId, newText, sender) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            messageElement.textContent = newText;
            messageElement.className = `message ${sender}-message`;
        }
        
        this.messages.push({ text: newText, sender });
    }
}

// Initialize AI Assistant when page loads
document.addEventListener('DOMContentLoaded', function() {
    new AIAssistant();
});