import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProgressProvider } from './contexts/ProgressContext';
import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { HomePage } from './pages/HomePage';
import { DashboardPage } from './pages/DashboardPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <ProgressProvider>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route 
              path="/" 
              element={
                <Layout showSidebar={false}>
                  <HomePage />
                </Layout>
              } 
            />
            <Route 
              path="/login" 
              element={
                <Layout showSidebar={false}>
                  <LoginForm onSuccess={() => window.location.href = '/dashboard'} />
                </Layout>
              } 
            />
            <Route 
              path="/register" 
              element={
                <Layout showSidebar={false}>
                  <RegisterForm onSuccess={() => window.location.href = '/dashboard'} />
                </Layout>
              } 
            />

            {/* Protected routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <DashboardPage />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            {/* Placeholder routes for future implementation */}
            <Route 
              path="/modules" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-semibold text-gray-900">Modules</h2>
                      <p className="text-gray-600 mt-2">Module listing will be implemented in future tasks</p>
                    </div>
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/modules/:moduleId" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-semibold text-gray-900">Module Details</h2>
                      <p className="text-gray-600 mt-2">Module details will be implemented in future tasks</p>
                    </div>
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/progress" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-semibold text-gray-900">Progress</h2>
                      <p className="text-gray-600 mt-2">Progress page will be implemented in future tasks</p>
                    </div>
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/bookmarks" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-semibold text-gray-900">Bookmarks</h2>
                      <p className="text-gray-600 mt-2">Bookmarks page will be implemented in future tasks</p>
                    </div>
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-semibold text-gray-900">Profile</h2>
                      <p className="text-gray-600 mt-2">Profile page will be implemented in future tasks</p>
                    </div>
                  </Layout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-semibold text-gray-900">Settings</h2>
                      <p className="text-gray-600 mt-2">Settings page will be implemented in future tasks</p>
                    </div>
                  </Layout>
                </ProtectedRoute>
              } 
            />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </ProgressProvider>
    </AuthProvider>
  );
}

export default App;