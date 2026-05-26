'use strict';

const mcpServer = require('/DataServcies/lib/mcp-server.sjs');

function handleMessage(message) {
  xdmp.log(`MCP Server Request received: ${JSON.stringify(message)}`, 'debug');
  
  try {
    const response = mcpServer.handleMessage(message);
    xdmp.log(`MCP Server Response: ${JSON.stringify(response)}`, 'debug');
    return response;
  } catch (error) {
    xdmp.log(`Error in MCP Server: ${error.stack}`, 'error');
    const requestId = message?.requestId || sem.uuidString();
    return {
      type: `${message?.type || 'error'}_response`,
      requestId: requestId,
      status: 'error',
      error: {
        code: 'INTERNAL_ERROR',
        message: error.message
      }
    };
  }
}

exports.handleMessage = handleMessage;
