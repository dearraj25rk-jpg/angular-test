import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable()
export class SecurityInterceptor implements HttpInterceptor {

  private readonly CSRF_HEADER_NAME = 'X-XSRF-TOKEN';
  private readonly CSRF_COOKIE_NAME = 'XSRF-TOKEN';

  intercept(req: HttpRequest<unknown>, next: HttpHandler) {
    let secureReq = req;

    // Add security headers for all requests
    const securityHeaders: Record<string, string> = {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    };

    // Add CSRF token for state-changing operations if enabled
    if (environment.security.enableCSRF && this.isStateChangingMethod(req.method)) {
      const csrfToken = this.getCSRFToken();
      if (csrfToken) {
        securityHeaders[this.CSRF_HEADER_NAME] = csrfToken;
      }
    }

    // Apply all security headers
    const headers = Object.keys(securityHeaders).reduce((acc, key) => {
      const value = securityHeaders[key];
      return value ? acc.set(key, value) : acc;
    }, req.headers);

    secureReq = req.clone({ headers });

    return next.handle(secureReq);
  }

  private isStateChangingMethod(method: string): boolean {
    return ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase());
  }

  private getCSRFToken(): string | null {
    // In a real application, this would extract the token from a cookie or meta tag
    // For now, we'll return a placeholder
    return this.getCookie(this.CSRF_COOKIE_NAME);
  }

  private getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() || null;
    }
    return null;
  }
}