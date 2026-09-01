import React from "react";
import { Navigate } from "react-router-dom";
import { useLTI } from "../contexts/LTIContext";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useLTI();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 text-sm text-gray-500">
        Checking session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}
