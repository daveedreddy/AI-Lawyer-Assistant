import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';

// Pages
import SplashScreen from './pages/SplashScreen';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import ChatScreen from './pages/ChatScreen';
import ChatHistory from './pages/ChatHistory';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import Help from './pages/Help';
import LegalDisclaimer from './pages/LegalDisclaimer';

// Protected Route Wrapper Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 font-semibold">Initializing Session...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <MainLayout>{children}</MainLayout>;
};

// Public Route Wrapper (Redirects to chat if logged in)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/chat" replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Redirect root path / to /chat */}
            <Route path="/" element={<SplashScreen />} />

            {/* Public Auth Routes */}
            <Route 
              path="/login" 
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              } 
            />
            <Route 
              path="/signup" 
              element={
                <PublicRoute>
                  <SignUp />
                </PublicRoute>
              } 
            />

            {/* Protected Application Routes */}
            <Route 
              path="/chat" 
              element={
                <ProtectedRoute>
                  <ChatScreen />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/chat/:id" 
              element={
                <ProtectedRoute>
                  <ChatScreen />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/history" 
              element={
                <ProtectedRoute>
                  <ChatHistory />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/help" 
              element={
                <ProtectedRoute>
                  <Help />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/disclaimer" 
              element={
                <ProtectedRoute>
                  <LegalDisclaimer />
                </ProtectedRoute>
              } 
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
