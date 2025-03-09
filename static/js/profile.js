document.addEventListener('DOMContentLoaded', function() {
    // Initialize clipboard.js
    new ClipboardJS('.copy-btn');

    // Form toggle functionality
    const showFormBtn = document.getElementById('showGenerateForm');
    const cancelBtn = document.getElementById('cancelGenerate');
    const generateForm = document.getElementById('generateKeyForm');

    if (showFormBtn && cancelBtn && generateForm) {
        showFormBtn.addEventListener('click', () => {
            generateForm.classList.add('active');
            showFormBtn.style.display = 'none';
        });

        cancelBtn.addEventListener('click', () => {
            generateForm.classList.remove('active');
            showFormBtn.style.display = 'block';
        });
    }

    // Copy button feedback
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', () => {
            const originalTitle = button.getAttribute('title');
            button.setAttribute('title', 'Copied!');
            
            setTimeout(() => {
                button.setAttribute('title', originalTitle);
            }, 2000);
        });
    });

    // Revoke API Key functionality
    document.querySelectorAll('.revoke-key-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const keyId = e.target.dataset.keyId;
            const keyName = e.target.dataset.keyName;
            
            if (confirm(`Are you sure you want to revoke the API key "${keyName}"? This action cannot be undone.`)) {
                try {
                    const response = await fetch(`/api/keys/${keyId}/revoke/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken(),
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    
                    if (!data.is_active) {
                        // Remove the API key item from the DOM
                        const keyItem = button.closest('.api-key-item');
                        keyItem.remove();

                        // Show success message
                        showNotification('API key revoked successfully', 'success');

                        // If no more keys, show empty state
                        const keysList = document.querySelector('.api-keys-list');
                        if (!keysList.querySelector('.api-key-item')) {
                            keysList.innerHTML = `
                                <div class="empty-state">
                                    <p>No API keys generated yet.</p>
                                </div>`;
                        }
                    } else {
                        throw new Error('Failed to revoke API key');
                    }
                } catch (error) {
                    console.error('Error revoking API key:', error);
                    showNotification('Failed to revoke API key', 'error');
                }
            }
        });
    });

    // Helper function to get CSRF token
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // Helper function to show notifications
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;

        // Add notification to the page
        const container = document.querySelector('.profile-container');
        container.insertBefore(notification, container.firstChild);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
});
