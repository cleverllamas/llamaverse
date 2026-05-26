'use strict';

// MCP Server Configuration
const config = {
  port: 8040,
  server: 'MCPServer',
  rootEndpoint: '/api',
  services: [
    {
      path: '/DataServcies/hello-world.sjs',
      endpoint: '/hello-world'
    }
  ]
};

exports.config = config;
