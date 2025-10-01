import { Injectable, ErrorHandler } from '@angular/core';
import { environment } from '../../../environments/environment';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  handleError(error: Error): void {
    const chunkFailedMessage = /Loading chunk [\d]+ failed/;

    if (chunkFailedMessage.test(error.message)) {
      if (environment.enableDebug) {
        console.error('Chunk loading failed. Reloading the page...');
      }
      window.location.reload();
      return;
    }

    if (environment.enableDebug) {
      console.error('An error occurred:', error);
    } else {
      // In production, send to logging service
      console.error('Application error:', error.message);
    }
  }
}
