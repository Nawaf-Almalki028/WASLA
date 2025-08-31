(function() {
    'use strict';
    
    let waslaIsOpen = false;
    let isTyping = false;
    
    // Get API URL from Django template
    const API_URL = window.WASLEH_BOT_API || '/support/chatbot/get-response/';
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeChatbot();
    });
    
    function initializeChatbot() {
        console.log('🚀 Wasla Chatbot initialized for Django');
        console.log('API URL:', API_URL);
        
        // Remove old chatbot if exists
        const oldChatbot = document.getElementById('chatbot-widget');
        if (oldChatbot) {
            oldChatbot.remove();
        }
        
        const oldButton = document.getElementById('chatbot-button');
        if (oldButton) {
            oldButton.remove();
        }
        
        // Add event listeners
        const input = document.getElementById('waslaMessageInput');
        const sendBtn = document.getElementById('waslaSendBtn');
        
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    waslaSendMessage();
                }
            });
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', waslaSendMessage);
        }
        
        // ESC key to close
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && waslaIsOpen) {
                waslaCloseChat();
            }
        });
        
        // Add quick responses after delay
        setTimeout(addQuickResponses, 1000);
    }
    
    // Toggle chat modal
    window.waslaToggleChat = function() {
        const modal = document.getElementById('waslaChatModal');
        const toggle = document.querySelector('.wasla-chat-toggle');
        
        if (waslaIsOpen) {
            modal.classList.remove('show');
            waslaIsOpen = false;
            if (toggle) toggle.innerHTML = '💬';
        } else {
            modal.classList.add('show');
            waslaIsOpen = true;
            if (toggle) toggle.innerHTML = '✕';
            setTimeout(() => {
                const input = document.getElementById('waslaMessageInput');
                if (input) input.focus();
            }, 300);
        }
    };
    
    // Close chat modal
    window.waslaCloseChat = function(event) {
        if (event && event.target !== event.currentTarget) return;
        
        const modal = document.getElementById('waslaChatModal');
        const toggle = document.querySelector('.wasla-chat-toggle');
        
        modal.classList.remove('show');
        waslaIsOpen = false;
        if (toggle) toggle.innerHTML = '💬';
    };
    
    // Get CSRF Token
    function getCookie(name) {
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
    
    // Send message function - Django Version
    window.waslaSendMessage = async function() {
        const input = document.getElementById('waslaMessageInput');
        const sendBtn = document.getElementById('waslaSendBtn');
        
        if (!input || !sendBtn) {
            console.error('Input or send button not found');
            return;
        }
        
        const message = input.value.trim();
        
        if (!message || sendBtn.disabled || isTyping) return;
        
        // Add user message
        waslaAddMessage(message, 'user');
        input.value = '';
        sendBtn.disabled = true;
        isTyping = true;
        waslaShowTyping();
        
        try {
            console.log('Sending message to:', API_URL);
            
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: getSessionId()
                })
            });
            
            console.log('Response status:', response.status);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            waslaHideTyping();
            
            if (response.ok && data.response) {
                waslaAddMessage(data.response, 'bot');
            } else if (data.error) {
                waslaAddMessage(`Sorry: ${data.error}`, 'bot');
            } else {
                waslaAddMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            waslaHideTyping();
            waslaAddMessage('Sorry, there was a connection error. Please check your internet connection and try again.', 'bot');
        } finally {
            sendBtn.disabled = false;
            isTyping = false;
        }
    };
    
    // Get or create session ID
    function getSessionId() {
        let sessionId = localStorage.getItem('wasla_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('wasla_session_id', sessionId);
        }
        return sessionId;
    }
    
    // Add message to chat
    function waslaAddMessage(text, type) {
        const messagesContainer = document.getElementById('waslaChatMessages');
        if (!messagesContainer) {
            console.error('Messages container not found');
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `wasla-message ${type}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'wasla-message-bubble';
        
        // Handle long messages
        if (text.length > 400) {
            const shortText = text.substring(0, 400) + '...';
            
            bubble.innerHTML = `
                <span class="short-text">${escapeHtml(shortText)}</span>
                <span class="full-text" style="display: none;">${escapeHtml(text)}</span>
                <br><button onclick="toggleMessage(this)" style="background: none; border: none; color: #60a5fa; cursor: pointer; font-size: 12px; margin-top: 5px;">Read more</button>
            `;
        } else {
            bubble.textContent = text;
        }
        
        messageDiv.appendChild(bubble);
        messagesContainer.appendChild(messageDiv);
        
        // Smooth scroll to bottom
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
    
    // Escape HTML to prevent XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // Toggle long message display
    window.toggleMessage = function(button) {
        const bubble = button.closest('.wasla-message-bubble');
        const shortText = bubble.querySelector('.short-text');
        const fullText = bubble.querySelector('.full-text');
        
        if (shortText.style.display === 'none') {
            shortText.style.display = 'inline';
            fullText.style.display = 'none';
            button.textContent = 'Read more';
        } else {
            shortText.style.display = 'none';
            fullText.style.display = 'inline';
            button.textContent = 'Read less';
        }
    };
    
    // Show typing indicator
    function waslaShowTyping() {
        const typing = document.getElementById('waslaTyping');
        if (typing) {
            typing.style.display = 'flex';
            
            const messagesContainer = document.getElementById('waslaChatMessages');
            if (messagesContainer) {
                setTimeout(() => {
                    messagesContainer.scrollTo({
                        top: messagesContainer.scrollHeight,
                        behavior: 'smooth'
                    });
                }, 50);
            }
        }
    }
    
    // Hide typing indicator
    function waslaHideTyping() {
        const typing = document.getElementById('waslaTyping');
        if (typing) {
            typing.style.display = 'none';
        }
    }
    
    // Quick responses
    window.sendQuickResponse = function(response) {
        const input = document.getElementById('waslaMessageInput');
        if (input) {
            input.value = response;
            waslaSendMessage();
        }
    };
    
    // Add quick response buttons
    function addQuickResponses() {
        const messagesContainer = document.getElementById('waslaChatMessages');
        if (!messagesContainer) return;
        
        // Check if already added
        if (messagesContainer.querySelector('.wasla-quick-responses')) return;
        
        const quickResponsesDiv = document.createElement('div');
        quickResponsesDiv.className = 'wasla-quick-responses';
        quickResponsesDiv.innerHTML = `
            <div style="margin: 15px 0; text-align: center;">
                <p style="color: #94a3b8; font-size: 12px; margin-bottom: 10px;">Quick questions:</p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                    <button onclick="sendQuickResponse('How do I register for the hackathon?')" class="quick-btn">📝 Registration</button>
                    <button onclick="sendQuickResponse('What are the prizes and awards?')" class="quick-btn">🏆 Prizes</button>
                    <button onclick="sendQuickResponse('What is the event schedule?')" class="quick-btn">📅 Schedule</button>
                    <button onclick="sendQuickResponse('How can I contact support?')" class="quick-btn">📞 Contact</button>
                    <button onclick="sendQuickResponse('What are the technical requirements?')" class="quick-btn">💻 Tech Info</button>
                </div>
            </div>
        `;
        
        // Add CSS for quick buttons if not already added
        if (!document.getElementById('quick-btn-styles')) {
            const style = document.createElement('style');
            style.id = 'quick-btn-styles';
            style.textContent = `
                .quick-btn {
                    background: rgba(59, 130, 246, 0.2);
                    border: 1px solid rgba(59, 130, 246, 0.4);
                    color: #93c5fd;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-size: 11px;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                .quick-btn:hover {
                    background: rgba(59, 130, 246, 0.3);
                    transform: translateY(-1px);
                    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
                }
                .quick-btn:active {
                    transform: translateY(0);
                }
            `;
            document.head.appendChild(style);
        }
        
        messagesContainer.appendChild(quickResponsesDiv);
    }
    
    // Handle connection status
    function handleConnectionStatus() {
        const toggle = document.querySelector('.wasla-chat-toggle');
        if (!toggle) return;
        
        if (navigator.onLine) {
            toggle.style.opacity = '1';
            toggle.title = 'Chat with Wasla Assistant';
        } else {
            toggle.style.opacity = '0.6';
            toggle.title = 'Chat unavailable - No internet connection';
        }
    }
    
    // Listen for online/offline events
    window.addEventListener('online', handleConnectionStatus);
    window.addEventListener('offline', handleConnectionStatus);
    
    // Initial connection check
    handleConnectionStatus();
    
    console.log('✅ Wasla Chatbot ready for Django!');
    
})();