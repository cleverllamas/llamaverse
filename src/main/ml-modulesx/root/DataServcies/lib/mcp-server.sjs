'use strict';

const serverInfo = {
  protocol: {
    name: "mcp",
    version: "1.0"
  },
  models: [{
    name: "hello-world",
    description: "A customizable greeting model with multi-language support",
    version: "1.0.0",
    parameters: {
      name: {
        type: "string",
        description: "Name to greet",
        optional: true,
        default: "World"
      },
      language: {
        type: "string",
        description: "Language for greeting",
        optional: true,
        default: "en",
        enum: ["en", "es", "fr"]
      },
      style: {
        type: "string",
        description: "Greeting style",
        optional: true,
        default: "formal",
        enum: ["formal", "casual", "friendly"]
      },
      format: {
        type: "string",
        description: "Response format",
        optional: true,
        default: "text",
        enum: ["text", "html", "json"]
      },
      includeEmoji: {
        type: "boolean",
        description: "Include emoji in greeting",
        optional: true,
        default: false
      }
    },
    capabilities: {
      streaming: false,
      tokenization: false
    }
  }],
  capabilities: {
    streamingSupported: false,
    maxConcurrentRequests: 1
  }
};

const greetings = {
  en: {
    formal: { text: 'Greetings', emoji: '👋' },
    casual: { text: 'Hey', emoji: '✌️' },
    friendly: { text: 'Hi', emoji: '😊' }
  },
  es: {
    formal: { text: 'Saludos', emoji: '👋' },
    casual: { text: 'Hola', emoji: '✌️' },
    friendly: { text: '¡Hola', emoji: '😊' }
  },
  fr: {
    formal: { text: 'Bonjour', emoji: '👋' },
    casual: { text: 'Salut', emoji: '✌️' },
    friendly: { text: 'Coucou', emoji: '😊' }
  }
};

function handleInitialize(requestId) {
  return {
    type: 'initialize_response',
    requestId: requestId,
    status: 'success',
    serverInfo: serverInfo
  };
}

function formatGreeting(inputs) {
  const name = inputs?.name || 'World';
  const language = inputs?.language || 'en';
  const style = inputs?.style || 'formal';
  const format = inputs?.format || 'text';
  const includeEmoji = inputs?.includeEmoji || false;

  const greeting = greetings[language]?.[style] || greetings.en.formal;
  const emojiSuffix = includeEmoji ? ` ${greeting.emoji}` : '';
  
  switch (format) {
    case 'html':
      return {
        content: `<h1>${greeting.text}, ${name}!${emojiSuffix}</h1>`,
        contentType: 'text/html'
      };
    case 'json':
      return {
        greeting: greeting.text,
        name: name,
        emoji: includeEmoji ? greeting.emoji : null,
        fullMessage: `${greeting.text}, ${name}!${emojiSuffix}`
      };
    default: // text
      return `${greeting.text}, ${name}!${emojiSuffix}`;
  }
}

function handleGenerate(message, requestId) {
  const formattedResponse = formatGreeting(message.inputs);
  
  return {
    type: 'generate_response',
    requestId: requestId,
    status: 'success',
    response: {
      message: formattedResponse,
      parameters: message.inputs || {},
      metadata: {
        timestamp: fn.currentDateTime(),
        server: xdmp.hostName(),
        supportedLanguages: Object.keys(greetings),
        supportedStyles: Object.keys(greetings.en),
        supportedFormats: ['text', 'html', 'json']
      }
    }
  };
}

function handleMessage(message) {
  if (!message?.type) {
    throw new Error('Invalid MCP message: missing type');
  }

  const requestId = message.requestId || sem.uuidString();

  switch (message.type) {
    case 'initialize':
      return handleInitialize(requestId);
    case 'generate':
      return handleGenerate(message, requestId);
    default:
      throw new Error(`Unsupported message type: ${message.type}`);
  }
}

exports.handleMessage = handleMessage;
