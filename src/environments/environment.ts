export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  enableLogging: true,
  logLevel: 'debug',
  features: {
    analytics: false,
    monitoring: false
  },
  security: {
    enableCSRF: true,
    tokenExpiration: 3600000, // 1 hour in milliseconds
    maxLoginAttempts: 3
  }
};