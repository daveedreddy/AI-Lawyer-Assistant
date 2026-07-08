import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Scale, Mail, Lock, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/useAuth';

const loginSchema = zod.object({
  email: zod.string().email('Please enter a valid email address'),
  password: zod.string().min(6, 'Password must be at least 6 characters long'),
});

type LoginFormValues = zod.infer<typeof loginSchema>;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, resetPassword } = useAuth();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resetSent, setResetSent] = useState(false);

  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data: LoginFormValues) => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await login(data.email, data.password);
      navigate('/chat');
    } catch (err: any) {
      setErrorMsg(err.message || 'We could not sign you in. Please check your details and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPassword = async () => {
    const email = getValues('email');
    if (!email || !email.includes('@')) {
      setErrorMsg('Enter your email address above, then choose Forgot Password.');
      return;
    }
    try {
      await resetPassword(email);
      setResetSent(true);
      setErrorMsg(null);
    } catch (err: any) {
      setErrorMsg(err.message || 'We could not send the reset email.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors duration-300">
      <div className="hidden md:flex md:w-1/2 bg-white dark:bg-gray-900 items-center justify-center p-12 relative overflow-hidden border-r border-gray-200 dark:border-gray-800">
        <div className="absolute inset-0 auth-backdrop-pattern opacity-80" />
        <div className="auth-rail absolute left-0 right-0 top-20 h-px" />
        <div className="auth-rail absolute left-0 right-0 bottom-24 h-px animation-delay-700" />

        <div className="relative max-w-lg space-y-6 animate-slide-up">
          <div className="p-3 bg-brand-500 text-white rounded-lg w-fit shadow-lg shadow-brand-500/20">
            <Scale size={32} />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight font-sans">
            Nyaya Samrakshan helps you understand what to do next
          </h2>
          <p className="text-gray-500 dark:text-gray-400 leading-relaxed text-sm">
            Ask in everyday words, review saved conversations, and turn confusing notices or agreements into clear next steps.
          </p>
          <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
            <p className="italic text-xs text-gray-500 dark:text-gray-400">
              For information and preparation. For urgent or personal matters, consult a qualified professional.
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md space-y-8 animate-slide-up">
          <div className="space-y-2">
            <div className="md:hidden p-3 bg-brand-500 text-white rounded-2xl w-fit mb-4">
              <Scale size={24} />
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Sign in to continue with Nyaya Samrakshan.
            </p>
          </div>

          {errorMsg && (
            <div className="flex items-center space-x-2.5 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs">
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          {resetSent && (
            <div className="flex items-center space-x-2.5 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs">
              <CheckCircle2 size={16} />
              <span>Password reset email sent. Please check your inbox.</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <Mail size={12} />
                <span>Email Address</span>
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                className={`custom-input ${errors.email ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('email')}
              />
              {errors.email && <p className="text-[10px] text-red-500 font-medium">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                  <Lock size={12} />
                  <span>Password</span>
                </label>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-[10px] text-brand-500 hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <input
                type="password"
                placeholder="Enter your password"
                className={`custom-input ${errors.password ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('password')}
              />
              {errors.password && <p className="text-[10px] text-red-500 font-medium">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center space-x-2 bg-brand-500 hover:bg-brand-600 text-white py-3 rounded-xl shadow-lg shadow-brand-500/15 hover:shadow-brand-500/25 active:scale-[0.99] disabled:opacity-50 transition-all duration-200 text-sm font-semibold"
            >
              <span>{isSubmitting ? 'Signing in...' : 'Sign in'}</span>
              {!isSubmitting && <ArrowRight size={16} />}
            </button>
          </form>

          <div className="text-center text-xs text-gray-500 dark:text-gray-400">
            New here?{' '}
            <Link to="/signup" className="text-brand-500 hover:underline font-semibold">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
