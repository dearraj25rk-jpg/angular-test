import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface User {
  username: string;
  token?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser: Observable<User | null>;

  constructor() {
    const storedUser = this.getStoredUser();
    this.currentUserSubject = new BehaviorSubject<User | null>(storedUser);
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  login(username: string, password: string): boolean {
    // In production, this would be an HTTP call to your backend
    if (username && password) {
      const user: User = { username, token: this.generateToken() };
      this.storeUser(user);
      this.currentUserSubject.next(user);
      return true;
    }
    return false;
  }

  logout(): void {
    this.removeStoredUser();
    this.currentUserSubject.next(null);
  }

  isAuthenticated(): boolean {
    return !!this.currentUserValue;
  }

  private generateToken(): string {
    return btoa(`${Date.now()}-${Math.random()}`);
  }

  private storeUser(user: User): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('currentUser', JSON.stringify(user));
    }
  }

  private getStoredUser(): User | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('currentUser');
      return stored ? JSON.parse(stored) : null;
    }
    return null;
  }

  private removeStoredUser(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('currentUser');
    }
  }
}
