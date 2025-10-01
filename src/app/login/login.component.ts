import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  standalone: false
})
export class LoginComponent {
  @Input() usernameLabel = 'Username';
  @Input() passwordLabel = 'Password';
  @Input() buttonLabel = 'Login';
  @Input() validateFn: ((username: string, password: string) => boolean) | null = null;
  @Output() loginSuccess = new EventEmitter<{ username: string }>();
  @Output() loginFail = new EventEmitter<void>();

  username = '';
  password = '';
  error = '';
  isLoading = false;
  returnUrl = '/dashboard';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {
    // Get return url from route parameters or default to dashboard
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';

    // Redirect to dashboard if already logged in
    if (this.authService.isAuthenticated()) {
      this.router.navigate([this.returnUrl]);
    }
  }

  login(): void {
    if (!this.username || !this.password) {
      this.error = 'Please enter username and password';
      return;
    }

    this.isLoading = true;
    this.error = '';

    try {
      const validate = this.validateFn || ((username: string, password: string) => username === 'test' && password === '123');

      if (validate(this.username, this.password)) {
        this.authService.login(this.username, this.password);
        this.loginSuccess.emit({ username: this.username });
        this.router.navigate([this.returnUrl]);
      } else {
        this.error = 'Invalid username or password';
        this.loginFail.emit();
      }
    } catch (error) {
      this.error = 'An error occurred during login';
      console.error('Login error:', error);
    } finally {
      this.isLoading = false;
    }
  }
}
