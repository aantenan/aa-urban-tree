import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ApplicationProvider } from './context/ApplicationContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppLayout } from './components/AppLayout';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { ApplicationFormPage } from './pages/ApplicationFormPage';
import { PublicListingPage } from './pages/PublicListingPage';
import { BoardReviewQueuePage } from './pages/BoardReviewQueuePage';
import { BoardApplicationDetailPage } from './pages/BoardApplicationDetailPage';
import { SessionTimeoutWarning } from './components/SessionTimeoutWarning';

function App() {
  return (
    <AuthProvider>
      <ApplicationProvider>
        <BrowserRouter>
          <SessionTimeoutWarning />
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/listing" element={<PublicListingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard/application"
                element={
                  <ProtectedRoute>
                    <ApplicationFormPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard/application/:id"
                element={
                  <ProtectedRoute>
                    <ApplicationFormPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/board/review"
                element={
                  <ProtectedRoute>
                    <BoardReviewQueuePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/board/review/:id"
                element={
                  <ProtectedRoute>
                    <BoardApplicationDetailPage />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ApplicationProvider>
    </AuthProvider>
  );
}

export default App;
