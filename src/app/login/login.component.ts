import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
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

  constructor(private router: Router) {}

  login() {
    const validate = this.validateFn || ((username: string, password: string) => username === 'test' && password === '123');
    if (validate(this.username, this.password)) {
      this.error = '';
      this.loginSuccess.emit({ username: this.username });
      this.router.navigate(['/dashboard']);
    } else {
      this.error = 'Invalid username or password';
      this.loginFail.emit();
    }
  }
}
