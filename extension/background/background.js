// Background script for JobBuddy Chrome Extension

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('JobBuddy Assistant installed');
});

// Listen for tab updates to show extension icon on job sites
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    // Check if we're on a job site
    const jobSites = [
      'linkedin.com/jobs',
      'indeed.com',
      'glassdoor.com',
      'monster.com'
    ];
    
    const isJobSite = jobSites.some(site => tab.url.includes(site));
    
    if (isJobSite) {
      // Show extension icon
      chrome.action.enable(tabId);
    } else {
      // Hide extension icon
      chrome.action.disable(tabId);
    }
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveJob') {
    // Save job to backend
    saveJobToBackend(request.data)
      .then(response => sendResponse({ success: true, data: response }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep message channel open for async response
  } else if (request.action === 'getUserData') {
    // Get user data from backend
    getUserDataFromBackend()
      .then(data => sendResponse({ success: true, data: data }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep message channel open for async response
  }
});

// Save job to backend
async function saveJobToBackend(jobData) {
  // In a real implementation, you would send this data to your backend API
  console.log('Saving job to backend:', jobData);
  
  // Example fetch call:
  /*
  const response = await fetch('http://localhost:8000/api/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + await getAuthToken()
    },
    body: JSON.stringify(jobData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to save job');
  }
  
  return await response.json();
  */
  
  // For now, just return a mock response
  return { id: Date.now(), ...jobData };
}

// Get user data from backend
async function getUserDataFromBackend() {
  // In a real implementation, you would fetch user data from your backend API
  console.log('Getting user data from backend');
  
  // Example fetch call:
  /*
  const response = await fetch('http://localhost:8000/api/auth/profile', {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + await getAuthToken()
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get user data');
  }
  
  return await response.json();
  */
  
  // For now, just return mock data
  return {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    address: '123 Main St, City, State 12345'
  };
}

// Get auth token (would be stored securely)
async function getAuthToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['authToken'], function(result) {
      resolve(result.authToken || '');
    });
  });
}