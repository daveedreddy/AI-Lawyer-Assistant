import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Scale, Mail, Lock, User, ShieldAlert, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/useAuth';

const signupSchema = zod.object({
  fullName: zod.string().min(3, 'Full name must be at least 3 characters'),
  email: zod.string().email('Please enter a valid email address'),
  barEnrollment: zod.string().min(5, 'Bar Enrollment ID is required (e.g. BCI/2023/1024)'),
  password: zod.string().min(6, 'Password must be at least 6 characters long'),
  confirmPassword: zod.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
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
      await signUp(data.fullName, data.email, data.barEnrollment, data.password);
      navigate('/chat');
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred during registration.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors duration-300">
      
      {/* Decorative Brand Panel */}
      <div className="hidden md:flex md:w-1/2 bg-gray-200 dark:bg-gray-900 items-center justify-center p-12 relative overflow-hidden border-r border-gray-300 dark:border-gray-800">
        <div className="absolute inset-0 flex items-center justify-center opacity-5">
          <Scale size={400} />
        </div>
        
        <div className="relative max-w-lg space-y-6">
          <div className="p-3 bg-brand-500 text-white rounded-2xl w-fit shadow-lg shadow-brand-500/20">
            <Scale size={32} />
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">
            Register Legal Practitioner Account
          </h2>
          <p className="text-gray-500 dark:text-gray-400 leading-relaxed text-sm">
            Join thousands of advocates using Indian AI legal insights. Store drafts, query local and federal judicial precedents, and receive structure analyses within seconds.
          </p>
          <div className="pt-4 border-t border-gray-300 dark:border-gray-800">
            <p className="italic text-xs text-gray-500 dark:text-gray-400">
              BCI regulatory guidelines are integrated within the system checks.
            </p>
          </div>
        </div>
      </div>

      {/* SignUp Form Panel */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 overflow-y-auto">
        <div className="w-full max-w-md space-y-8 py-8 animate-slide-up">
          {/* Header */}
          <div className="space-y-2">
            <div className="md:hidden p-3 bg-brand-500 text-white rounded-2xl w-fit mb-4">
              <Scale size={24} />
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Create Account</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Provide your details to register as a verified legal consultant.
            </p>
          </div>

          {errorMsg && (
            <div className="flex items-center space-x-2.5 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs">
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <User size={12} />
                <span>Full Name</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Adv. Rajesh Sharma"
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
                <span>Email Address</span>
              </label>
              <input
                type="email"
                placeholder="e.g. advocate.sharma@legal.in"
                className={`custom-input ${errors.email ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('email')}
              />
              {errors.email && (
                <p className="text-[10px] text-red-500 font-medium">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <ShieldAlert size={12} />
                <span>Bar Enrollment ID</span>
              </label>
              <input
                type="text"
                placeholder="e.g. BCI/2015/8472"
                className={`custom-input ${errors.barEnrollment ? 'border-red-500 focus:ring-red-500' : ''}`}
                {...register('barEnrollment')}
              />
              {errors.barEnrollment && (
                <p className="text-[10px] text-red-500 font-medium">{errors.barEnrollment.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center space-x-1.5">
                <Lock size={12} />
                <span>Password</span>
              </label>
              <input
                type="password"
                placeholder="••••••••"
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
                placeholder="••••••••"
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
              className="w-full flex items-center justify-center space-x-2 bg-brand-500 hover:bg-brand-600 text-white py-3 rounded-xl shadow-lg shadow-brand-500/15 hover:shadow-brand-500/25 active:scale-[0.99] disabled:opacity-50 transition-all duration-200 text-sm font-semibold pt-4"
            >
              <span>{isSubmitting ? 'Registering...' : 'Register Account'}</span>
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
