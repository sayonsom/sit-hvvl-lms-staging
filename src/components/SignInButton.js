import React from 'react';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../authConfig';

const SignInButton = () => {
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch(e => {
      // Handle errors here, such as by alerting the user
      console.error(e);
    });
  };

  return <button onClick={handleLogin}>Sign In</button>;
};

export default SignInButton;
