document.addEventListener('DOMContentLoaded', function() {
  const parseJobButton = document.getElementById('parseJob');
  const autoFillButton = document.getElementById('autoFill');
  const statusElement = document.getElementById('status');

  // Update status text
  function updateStatus(text) {
    statusElement.textContent = text;
  }

  // Parse current job
  parseJobButton.addEventListener('click', async function() {
    updateStatus('Parsing job...');
    
    try {
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Send message to content script
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: 'parseJob'
      });
      
      if (response && response.success) {
        updateStatus('Job parsed successfully!');
      } else {
        updateStatus('Failed to parse job');
      }
    } catch (error) {
      console.error('Error parsing job:', error);
      updateStatus('Error parsing job');
    }
  });

  // Auto-fill application
  autoFillButton.addEventListener('click', async function() {
    updateStatus('Auto-filling application...');
    
    try {
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Send message to content script
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: 'autoFill'
      });
      
      if (response && response.success) {
        updateStatus('Application auto-filled!');
      } else {
        updateStatus('Failed to auto-fill application');
      }
    } catch (error) {
      console.error('Error auto-filling application:', error);
      updateStatus('Error auto-filling application');
    }
  });
});