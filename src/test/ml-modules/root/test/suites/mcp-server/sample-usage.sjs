'use strict';

const test = require('/test/test-helper.sjs');
const mcpService = require('/DataServcies/hello-world.sjs');

// Sample 1: Initialize request
const initializeRequest = {
  type: 'initialize',
  requestId: 'init-123'
};

// Sample 2: Basic greeting
const basicGreetingRequest = {
  type: 'generate',
  requestId: 'gen-123',
  inputs: {
    name: 'Alice'
  }
};

// Sample 3: Spanish formal greeting with emoji
const spanishFormalRequest = {
  type: 'generate',
  requestId: 'gen-456',
  inputs: {
    name: 'Carlos',
    language: 'es',
    style: 'formal',
    includeEmoji: true
  }
};

// Sample 4: French casual greeting in HTML format
const frenchHtmlRequest = {
  type: 'generate',
  requestId: 'gen-789',
  inputs: {
    name: 'Marie',
    language: 'fr',
    style: 'casual',
    format: 'html'
  }
};

// Sample 5: JSON response with all options
const jsonFullRequest = {
  type: 'generate',
  requestId: 'gen-abc',
  inputs: {
    name: 'David',
    language: 'en',
    style: 'friendly',
    format: 'json',
    includeEmoji: true
  }
};

// Run the samples
function runSamples() {
  const samples = [
    { name: 'Initialize Request', request: initializeRequest },
    { name: 'Basic Greeting', request: basicGreetingRequest },
    { name: 'Spanish Formal with Emoji', request: spanishFormalRequest },
    { name: 'French HTML Greeting', request: frenchHtmlRequest },
    { name: 'Full JSON Response', request: jsonFullRequest }
  ];

  samples.forEach(sample => {
    xdmp.log(`\n=== Running ${sample.name} ===`, 'info');
    xdmp.log(`Request: ${JSON.stringify(sample.request, null, 2)}`, 'info');
    
    const response = mcpService.handleMessage(sample.request);
    xdmp.log(`Response: ${JSON.stringify(response, null, 2)}`, 'info');
    
    // Add some basic assertions
    test.assertTrue(
      response.status === 'success',
      `${sample.name} should succeed`
    );
    test.assertEqual(
      response.requestId,
      sample.request.requestId,
      `${sample.name} should return matching requestId`
    );
  });
}

// Run all samples
runSamples();
