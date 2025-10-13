import { Injectable } from '@angular/core';

export enum LogLevel {
  Debug = 0,
  Info = 1,
  Warn = 2,
  Error = 3
}

@Injectable({
  providedIn: 'root'
})
export class LoggerService {
  private currentLogLevel = LogLevel.Info; // Set based on environment

  setLogLevel(level: LogLevel): void {
    this.currentLogLevel = level;
  }

  debug(message: string, data?: any): void {
    this.log(LogLevel.Debug, message, data);
  }

  info(message: string, data?: any): void {
    this.log(LogLevel.Info, message, data);
  }

  warn(message: string, data?: any): void {
    this.log(LogLevel.Warn, message, data);
  }

  error(message: string, error?: any): void {
    this.log(LogLevel.Error, message, error);
  }

  private log(level: LogLevel, message: string, data?: any): void {
    if (level < this.currentLogLevel) {
      return;
    }

    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${LogLevel[level]}] ${message}`;

    switch (level) {
      case LogLevel.Debug:
        console.debug(logMessage, data);
        break;
      case LogLevel.Info:
        console.info(logMessage, data);
        break;
      case LogLevel.Warn:
        console.warn(logMessage, data);
        break;
      case LogLevel.Error:
        console.error(logMessage, data);
        break;
    }

    // In production, send logs to external service
    if (level >= LogLevel.Error) {
      this.sendToLoggingService(level, message, data);
    }
  }

  private sendToLoggingService(level: LogLevel, message: string, data?: any): void {
    // Implementation for external logging service
    // e.g., POST to logging endpoint
  }
}