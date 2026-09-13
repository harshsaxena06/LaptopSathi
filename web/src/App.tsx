import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { ThemeProvider } from '@/context/ThemeContext';
import { ToastProvider } from '@/context/ToastContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { RoleGuard } from '@/components/RoleGuard';

import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { AboutPage } from '@/pages/AboutPage';
import { TermsPage } from '@/pages/TermsPage';
import { PrivacyPage } from '@/pages/PrivacyPage';
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/ResetPasswordPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { AdminDashboardPage } from '@/pages/AdminDashboardPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { SearchPage } from '@/pages/SearchPage';
import { RecommendPage } from '@/pages/RecommendPage';
import { ComparePage } from '@/pages/ComparePage';
import { BudgetOptimizerPage } from '@/pages/BudgetOptimizerPage';
import { SavedLaptopsPage } from '@/pages/SavedLaptopsPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/admin-login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/terms" element={<TermsPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/recommend" element={<RecommendPage />} />
                <Route path="/compare" element={<ComparePage />} />
                <Route path="/budget" element={<BudgetOptimizerPage />} />
                <Route path="/saved" element={<SavedLaptopsPage />} />

                <Route element={<RoleGuard allowedRoles={['admin']} />}>
                  <Route path="/admin" element={<AdminDashboardPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                </Route>
              </Route>

              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ToastProvider>
    </ThemeProvider>
  );
}
