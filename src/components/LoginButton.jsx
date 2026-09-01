import React from "react";
import { Button } from './button'

const LoginButton = () => {
  return (
    <div className="text-center max-w-md mx-auto">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <svg className="mx-auto h-12 w-12 text-blue-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          Access via Brightspace
        </h3>
        <p className="text-blue-700 mb-3">
          This application must be launched from your course in SIT Brightspace.
        </p>
        <p className="text-sm text-blue-600">
          Please navigate to your course and click the Virtual Lab link.
        </p>
      </div>
    </div>
  );
};

export default LoginButton;
