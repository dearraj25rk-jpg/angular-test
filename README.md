# Angular Test Application

Production-ready Angular 20.3.0 application with login and dashboard features.

## Features

- Angular 20.3.0 (non-standalone components)
- TypeScript 5.8.3
- Server-Side Rendering (SSR) with Express
- Production-ready configuration
- Authentication service with route guards
- Global error handling
- HTTP error interceptor
- Environment-based configuration

## Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)

## Installation

```bash
npm install
```

## Development

Start the development server:

```bash
npm start
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Build

Build the project for production:

```bash
npm run build:prod
```

The build artifacts will be stored in the `dist/` directory.

## Production Server

Run the production SSR server:

```bash
npm run prod
```

Or separately:

```bash
npm run build:prod
npm run serve:ssr
```

## Testing

Run unit tests:

```bash
npm test
```

Run headless tests:

```bash
npm run test:headless
```

## Login Credentials

For testing purposes, use:
- Username: `test`
- Password: `123`

## Project Structure

```
src/
├── app/
│   ├── core/
│   │   ├── guards/        # Route guards
│   │   ├── interceptors/  # HTTP interceptors
│   │   └── services/      # Core services
│   ├── dashboard/         # Dashboard module
│   ├── login/            # Login module
│   └── app.module.ts     # Root module
├── environments/         # Environment configurations
└── assets/              # Static assets
```

## Production Features

- Optimized bundle sizes
- Output hashing for cache busting
- Source maps disabled in production
- License extraction
- Environment-specific configurations
- Global error handling
- HTTP retry mechanism
- Authentication state management

## Bundle Size

- Initial bundle: ~346 KB (raw) / ~94 KB (gzipped)
- Main bundle: ~311 KB (raw) / ~82 KB (gzipped)
- Polyfills: ~35 KB (raw) / ~11 KB (gzipped)

## Angular Configuration

The application uses non-standalone components (NgModule-based architecture) as specified in `angular.json`:

```json
"schematics": {
  "@schematics/angular:component": {
    "standalone": false
  }
}
```

## Further Help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
