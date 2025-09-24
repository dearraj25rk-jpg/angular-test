export const environment = {
  production: true,
  apiUrl: 'https://api.yourapp.com/api',
  enableLogging: false,
  logLevel: 'error',
  features: {
    analytics: true,
    monitoring: true
  },
  security: {
    enableCSRF: true,
    tokenExpiration: 1800000, // 30 minutes in milliseconds
    maxLoginAttempts: 5
  }
};