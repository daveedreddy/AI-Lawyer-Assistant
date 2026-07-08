import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Scale, Mail, Lock, User, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/useAuth';

const signupSchema = zod.object({
  fullName: zod.string().min(3, 'Please enter your full name'),
  email: zod.string().email('Please enter a valid email address'),
  password: zod.string().min(6, 'Password must be at least 6 characters long'),
  confirmPassword: zod.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type SignupFormValues = zod.infer<typeof signupSchema>;

const SignUp: React.FC = () => {
  const navigate = useNavigate();
  const { signUp } = useAuth();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: SignupFormValues) => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await signUp(data.fullName, data.email, data.password);
      navigate('/chat');
    } catch (err: any) {
      setErrorMsg(err.message || 'We could not create your account. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors duration-300">
      <div className="hidden md:flex md:w-1/2 bg-white dark:bg-gray-900 items-center justify-center p-12 relative overflow-hidden border-r border-gray-200 dark:border-gray-800">
        <div className="absolute inset-0 auth-backdrop-pattern opacity-80" />
        <div className="auth-rail absolute left-0 right-0 top-24 h-px" />
        <div className="auth-rail absolute left-0 right-0 bottom-20 h-px animation-delay-700" />

        <div className="relative max-w-lg space-y-6 animate-slide-up">
          <div className="p-3 bg-brand-500 text-white rounded-lg w-fit shadow-lg shadow-brand-500/20">
            <Scale size={32} />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">
            Start with a simple question, not legal jargon
          </h2>
          <p className="text-gray-500 dark:text-gray-400 leading-relaxed text-sm">
            Create a secure account to ask everyday legal questions, save helpful answers, and review documents without any professional registration.
          </p>
          <div className="pt-4 border-t border-gray-200 dark:border-gray-800 flex items-start space-x-2 text-xs text-gray-500 dark:text-gray-400">
            <ShieldCheck size={16} className="text-emerald-500 shrink-0 mt-0.5" />
            <p>Your questions stay tied to your private account and can be revisited later.</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 overflow-y-auto">
        <div className="w-full max-w-md space-y-8 py-8 animate-slide-up">
          <div className="space-y-2">
            <div className="md:hidden p-3 bg-brand-500 text-white rounded-2xl w-fit mb-4">
              <Scale size={24} />
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Create your account</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Use your name, email, and a password. No BCI or advocate registration number is required.
            </p>
          </div>

          {errorMsg && (
            <div className="flex items-center space-x-2.5 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs">
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <User size={12} />
                <span>Full name</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Ananya Rao"
                className={`custom-input ${errors.fullName ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('fullName')}
              />
              {errors.fullName && (
                <p className="text-[10px] text-red-500 font-medium">{errors.fullName.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <Mail size={12} />
                <span>Email address</span>
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                className={`custom-input ${errors.email ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('email')}
              />
              {errors.email && (
                <p className="text-[10px] text-red-500 font-medium">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <Lock size={12} />
                <span>Password</span>
              </label>
              <input
                type="password"
                placeholder="At least 6 characters"
                className={`custom-input ${errors.password ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('password')}
              />
              {errors.password && (
                <p className="text-[10px] text-red-500 font-medium">{errors.password.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <Lock size={12} />
                <span>Confirm Password</span>
              </label>
              <input
                type="password"
                placeholder="Repeat your password"
                className={`custom-input ${errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('confirmPassword')}
              />
              {errors.confirmPassword && (
                <p className="text-[10px] text-red-500 font-medium">{errors.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center space-x-2 bg-brand-500 hover:bg-brand-600 text-white py-3 rounded-xl shadow-lg shadow-brand-500/15 hover:shadow-brand-500/25 active:scale-[0.99] disabled:opacity-50 transition-all duration-200 text-sm font-semibold"
            >
              <span>{isSubmitting ? 'Creating account...' : 'Create account'}</span>
              {!isSubmitting && <ArrowRight size={16} />}
            </button>
          </form>

          <div className="text-center text-xs text-gray-500 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-500 hover:underline font-semibold">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
