import React from 'react';

const TestComponent = () => {
  return React.createElement('div', null, 
    React.createElement('h1', null, 'Test Component'),
    React.createElement('p', null, 'This is a test component to verify JSX is working')
  );
};

export default TestComponent;