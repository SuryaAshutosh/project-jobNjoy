// Content script for JobBuddy Chrome Extension

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'parseJob') {
    // Parse job details from current page
    const jobDetails = parseJobDetails();
    sendResponse({ success: true, data: jobDetails });
  } else if (request.action === 'autoFill') {
    // Auto-fill application form
    autoFillApplication();
    sendResponse({ success: true });
  }
});

// Parse job details from the current page
function parseJobDetails() {
  // This is a simplified example - in reality, you'd need to adapt this
  // to work with specific job sites like LinkedIn, Indeed, etc.
  
  const title = document.querySelector('h1')?.textContent || '';
  const company = document.querySelector('[data-company]')?.textContent || '';
  const location = document.querySelector('[data-location]')?.textContent || '';
  const description = document.querySelector('[data-description]')?.textContent || '';
  
  return {
    title,
    company,
    location,
    description
  };
}

// Auto-fill application form
function autoFillApplication() {
  // This is a simplified example - in reality, you'd need to adapt this
  // to work with specific job application forms
  
  // Get user data from storage (would be populated from backend)
  chrome.storage.local.get(['userData'], function(result) {
    const userData = result.userData;
    
    if (userData) {
      // Fill common form fields
      fillField('firstName', userData.firstName);
      fillField('lastName', userData.lastName);
      fillField('email', userData.email);
      fillField('phone', userData.phone);
      fillField('address', userData.address);
      
      // Upload resume if file input is found
      uploadResume();
    }
  });
}

// Fill a form field by name or common selectors
function fillField(fieldName, value) {
  if (!value) return;
  
  const selectors = [
    `[name="${fieldName}"]`,
    `[id="${fieldName}"]`,
    `#${fieldName}`,
    `.${fieldName}`,
    `[data-testid="${fieldName}"]`,
    `input[placeholder*="${fieldName}" i]`
  ];
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      element.value = value;
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      break;
    }
  }
}

// Upload resume file
function uploadResume() {
  // This would typically involve getting a file URL from the backend
  // and programmatically uploading it to the form
  console.log('Resume upload functionality would go here');
}