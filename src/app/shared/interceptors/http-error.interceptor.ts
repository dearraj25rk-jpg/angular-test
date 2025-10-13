import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpErrorResponse } from '@angular/common/http';
import { catchError, retry } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { ErrorHandlerService } from '../services/error-handler.service';
import { LoggerService } from '../services/logger.service';

@Injectable()
export class HttpErrorInterceptor implements HttpInterceptor {

  constructor(
    private errorHandler: ErrorHandlerService,
    private logger: LoggerService
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    return next.handle(req).pipe(
      retry(1), // Retry failed requests once
      catchError((error: HttpErrorResponse) => {
        this.logger.error('HTTP Request Failed', {
          url: req.url,
          method: req.method,
          status: error.status,
          statusText: error.statusText
        });

        return this.errorHandler.handleError(error);
      })
    );
  }
}