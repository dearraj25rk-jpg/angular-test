import { ChangeDetectionStrategy, ChangeDetectorRef, Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoggerService } from '../shared/services/logger.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss'],
    standalone: false,
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class LoginComponent implements OnInit {
  @Input() usernameLabel = 'Username';
  @Input() passwordLabel = 'Password';
  @Input() buttonLabel = 'Login';
  @Input() validateFn: ((username: string, password: string) => boolean) | null = null;
  @Output() loginSuccess = new EventEmitter<{ username: string }>();
  @Output() loginFail = new EventEmitter<void>();

  loginForm!: FormGroup;
  error = '';
  isSubmitting = false;

  constructor(
    private router: Router,
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef,
    private logger: LoggerService
  ) {}

  ngOnInit(): void {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(3)]]
    });
  }

  get username() { return this.loginForm.get('username'); }
  get password() { return this.loginForm.get('password'); }

  getFieldError(fieldName: string): string {
    const field = this.loginForm.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
      }
      if (field.errors['minlength']) {
        return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least ${field.errors['minlength'].requiredLength} characters`;
      }
    }
    return '';
  }

  login(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this.cdr.markForCheck();
      return;
    }

    this.isSubmitting = true;
    this.error = '';
    this.cdr.markForCheck();

    const { username, password } = this.loginForm.value;
    this.logger.info('Login attempt', { username });

    // Simulate async operation
    setTimeout(() => {
      const validate = this.validateFn || ((u: string, p: string) => u === 'test' && p === '123');

      if (validate(username, password)) {
        this.logger.info('Login successful', { username });
        this.loginSuccess.emit({ username });
        this.router.navigate(['/dashboard']);
      } else {
        this.error = 'Invalid username or password';
        this.logger.warn('Login failed', { username });
        this.loginFail.emit();
      }

      this.isSubmitting = false;
      this.cdr.markForCheck();
    }, 1000);
  }
}
