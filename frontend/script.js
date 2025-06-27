// AI Document Q&A System - Frontend JavaScript

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
let authToken = localStorage.getItem('authToken');
let currentUser = null;
let currentDocument = null;
let currentDocumentName = null;

// Bootstrap Modal Instances
let loginModal, registerModal, uploadModal;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    setupEventListeners();
    checkAuthStatus();
});

// Initialize Bootstrap modals
function initializeModals() {
    loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
    uploadModal = new bootstrap.Modal(document.getElementById('uploadModal'));
}

// Setup event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Register form
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // File upload
    setupFileUpload();
    
    // Q&A input
    setupQAInput();
}

// Setup Q&A input functionality
function setupQAInput() {
    const questionInput = document.getElementById('questionInput');
    
    // Enter key to send question
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            askQuestion();
        }
    });
}

// Check authentication status
function checkAuthStatus() {
    if (authToken) {
        updateUIForAuthenticatedUser();
    } else {
        updateUIForUnauthenticatedUser();
    }
}

// Update UI for authenticated user
function updateUIForAuthenticatedUser() {
    const navbar = document.querySelector('.navbar-nav');
    navbar.innerHTML = `
        <span class="navbar-text text-light me-3">
            <i class="fas fa-user me-1"></i>Welcome, ${currentUser?.full_name || 'User'}
        </span>
        <button class="btn btn-outline-light" onclick="logout()">
            <i class="fas fa-sign-out-alt me-1"></i>Logout
        </button>
    `;
}

// Update UI for unauthenticated user
function updateUIForUnauthenticatedUser() {
    const navbar = document.querySelector('.navbar-nav');
    navbar.innerHTML = `
        <button class="btn btn-outline-light" onclick="showLoginModal()">
            <i class="fas fa-sign-in-alt me-1"></i>Login
        </button>
        <button class="btn btn-light ms-2" onclick="showRegisterModal()">
            <i class="fas fa-user-plus me-1"></i>Register
        </button>
    `;
}

// Show login modal
function showLoginModal() {
    loginModal.show();
}

// Show register modal
function showRegisterModal() {
    registerModal.show();
}

// Show upload modal
function showUploadModal() {
    if (!authToken) {
        showToast('Please login first to upload documents', 'warning');
        showLoginModal();
        return;
    }
    uploadModal.show();
}

// Show features section
function showFeatures() {
    const featuresSection = document.getElementById('features');
    featuresSection.style.display = 'block';
    featuresSection.scrollIntoView({ behavior: 'smooth' });
}

// Show Q&A section
function showQASection() {
    const qaSection = document.getElementById('qaSection');
    qaSection.style.display = 'block';
    qaSection.scrollIntoView({ behavior: 'smooth' });
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login/access-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            currentUser = { email: email };
            
            loginModal.hide();
            showToast('Login successful!', 'success');
            checkAuthStatus();
        } else {
            showToast(data.detail || data.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Handle register
async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_name: name,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            registerModal.hide();
            showToast('Registration successful! Please login.', 'success');
            showLoginModal();
        } else {
            showToast(data.detail || data.message || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Setup file upload functionality
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // File selection
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}

// Handle file upload
async function handleFileUpload(file) {
    if (!authToken) {
        showToast('Please login first', 'warning');
        return;
    }

    // Show progress
    const uploadArea = document.getElementById('uploadArea');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = uploadProgress.querySelector('.progress-bar');

    uploadArea.style.display = 'none';
    uploadProgress.style.display = 'block';

    // Prepare form data for backend upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
            method: 'POST',
            headers: {
                ...(authToken && { 'Authorization': `Bearer ${authToken}` })
            },
            body: formData
        });
        const data = await response.json();

        if (response.ok && data.document_id) {
            currentDocument = data.document_id;
            currentDocumentName = file.name;
            updateDocumentInfo();
            showQASection();
            enableQAInput();
            showToast(`File "${file.name}" uploaded successfully! You can now ask questions.`, 'success');
        } else {
            showToast(data.detail || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        uploadProgress.style.display = 'none';
        uploadArea.style.display = 'block';
        uploadModal.hide();
    }
}

// Update document info in Q&A header
function updateDocumentInfo() {
    const documentInfo = document.getElementById('currentDocument');
    documentInfo.textContent = currentDocumentName || 'No document uploaded';
}

// Enable Q&A input
function enableQAInput() {
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    
    questionInput.disabled = false;
    askButton.disabled = false;
    questionInput.focus();
}

// Ask question function
async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();

    if (!question) {
        showToast('Please enter a question', 'warning');
        return;
    }

    if (!currentDocument) {
        showToast('Please upload a document first', 'warning');
        return;
    }

    // Add user message to chat
    addMessageToChat('user', question);
    questionInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    try {
        // Call your backend API
        const response = await fetch(`${API_BASE_URL}/api/v1/questions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken && { 'Authorization': `Bearer ${authToken}` })
            },
            body: JSON.stringify({
                question_text: question,
                document_id: currentDocument,
                metadata: {} // Always include metadata as an object
            })
        });

        const data = await response.json();
        hideTypingIndicator();

        if (response.ok && data.answer_text) {
            addMessageToChat('assistant', data.answer_text);
        } else {
            addMessageToChat('assistant', data.detail || data.message || 'Sorry, I could not get an answer from the backend.');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('assistant', 'Network error. Please try again.');
    }
}

// Add message to chat
function addMessageToChat(sender, message) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Remove welcome message if it's the first real message
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar ${sender}">
            <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-bubble ${sender}">
            <div class="message-content">${message}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const chatContainer = document.getElementById('chatContainer');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message assistant';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar assistant">
            <i class="fas fa-robot"></i>
        </div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Logout function
function logout() {
    authToken = null;
    currentUser = null;
    currentDocument = null;
    currentDocumentName = null;
    localStorage.removeItem('authToken');
    showToast('Logged out successfully', 'success');
    checkAuthStatus();
    
    // Reset Q&A interface
    resetQAInterface();
}

// Reset Q&A interface
function resetQAInterface() {
    const qaSection = document.getElementById('qaSection');
    const chatContainer = document.getElementById('chatContainer');
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    
    qaSection.style.display = 'none';
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <i class="fas fa-lightbulb fa-2x text-warning mb-3"></i>
            <h5>Welcome to Document Q&A!</h5>
            <p>Upload a document and start asking questions. I'll help you understand the content using AI.</p>
            <div class="example-questions">
                <h6>Example questions:</h6>
                <ul class="list-unstyled">
                    <li><i class="fas fa-arrow-right me-2"></i>"What is the main topic of this document?"</li>
                    <li><i class="fas fa-arrow-right me-2"></i>"Summarize the key points"</li>
                    <li><i class="fas fa-arrow-right me-2"></i>"What are the main conclusions?"</li>
                </ul>
            </div>
        </div>
    `;
    questionInput.disabled = true;
    askButton.disabled = true;
    updateDocumentInfo();
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    
    // Set title and icon based on type
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    const titles = {
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        info: 'Information'
    };
    
    toastTitle.innerHTML = `<i class="${icons[type]} me-2"></i>${titles[type]}`;
    toastBody.textContent = message;
    
    // Add appropriate classes
    toast.className = `toast ${type}`;
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// API helper function
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        }
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    return response.json();
}

// Test API connection
async function testApiConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('API Status:', data);
        return data.status === 'healthy';
    } catch (error) {
        console.error('API connection failed:', error);
        return false;
    }
}

// Initialize API connection test
testApiConnection().then(isConnected => {
    if (!isConnected) {
        showToast('Cannot connect to API server. Please ensure the backend is running.', 'error');
    }
});

// Expose modal and feature functions to global scope for HTML onclick handlers
window.showLoginModal = showLoginModal;
window.showRegisterModal = showRegisterModal;
window.showFeatures = showFeatures;
window.showUploadModal = showUploadModal; 