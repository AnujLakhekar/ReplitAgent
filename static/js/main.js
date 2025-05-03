// Main JavaScript for Replit Agent

// Show confirmation modal for destructive actions
function confirmAction(message, callback) {
  if (confirm(message)) {
    callback();
  }
}

// Display flash messages
function showAlert(message, type = 'success') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = 'alert';
  
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  const container = document.querySelector('.container');
  container.insertBefore(alertDiv, container.firstChild);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    const bsAlert = new bootstrap.Alert(alertDiv);
    bsAlert.close();
  }, 5000);
}

// Copy text to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showAlert('Copied to clipboard!', 'info');
  }).catch(err => {
    console.error('Failed to copy text: ', err);
    showAlert('Failed to copy to clipboard', 'danger');
  });
}

// Format code based on language
function formatCode(code, language) {
  if (typeof hljs !== 'undefined') {
    const highlighted = hljs.highlight(code, { language: language }).value;
    return highlighted;
  }
  return code;
}

// Generic fetch wrapper with error handling
async function fetchAPI(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API request failed with status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API fetch error:', error);
    showAlert(error.message, 'danger');
    throw error;
  }
}

// Load file content into editor
async function loadFileContent(path, editorId) {
  try {
    const response = await fetchAPI(`/api/file/read?path=${encodeURIComponent(path)}`);
    if (response.status === 'success') {
      const editor = document.getElementById(editorId);
      if (editor) {
        editor.value = response.content;
      }
    }
  } catch (error) {
    console.error('Error loading file content:', error);
  }
}

// Save file content from editor
async function saveFileContent(path, editorId) {
  try {
    const editor = document.getElementById(editorId);
    if (!editor) return;
    
    const content = editor.value;
    const response = await fetchAPI('/api/file/write', {
      method: 'POST',
      body: JSON.stringify({ path, content })
    });
    
    if (response.status === 'success') {
      showAlert(`File ${path} saved successfully!`, 'success');
    }
  } catch (error) {
    console.error('Error saving file content:', error);
  }
}

// Execute code
async function executeCode(code, language) {
  try {
    const response = await fetchAPI('/api/code/execute', {
      method: 'POST',
      body: JSON.stringify({ code, language })
    });
    
    return response;
  } catch (error) {
    console.error('Error executing code:', error);
    return { status: 'error', message: error.message };
  }
}

// Initialize components when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  
  // Initialize code editors if CodeMirror is available
  if (typeof CodeMirror !== 'undefined') {
    document.querySelectorAll('.code-editor').forEach(editorElement => {
      const mode = editorElement.dataset.mode || 'python';
      CodeMirror.fromTextArea(editorElement, {
        lineNumbers: true,
        mode: mode,
        theme: 'darcula',
        indentUnit: 4,
        smartIndent: true,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        extraKeys: { "Tab": "insertSoftTab" }
      });
    });
  }
  
  // Initialize feather icons
  if (typeof feather !== 'undefined') {
    feather.replace();
  }
});
