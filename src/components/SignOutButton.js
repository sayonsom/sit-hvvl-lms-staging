import React from 'react';
import { useMsal } from '@azure/msal-react';

const SignOutButton = () => {
  const { instance } = useMsal();

  const handleLogout = () => {
    instance.logoutPopup().catch(e => {
      // Handle errors here
      console.error(e);
    });
  };

  return <button onClick={handleLogout}>Sign Out</button>;
};

export default SignOutButton;
