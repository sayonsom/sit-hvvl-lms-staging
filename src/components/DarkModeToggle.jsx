import React, { useState, useEffect } from 'react';
import { Switch, SwitchField } from './switch'

const DarkModeToggle = () => {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (localStorage.getItem('darkMode') === 'true') {
      document.documentElement.classList.add('dark');
      setDarkMode(true);
    }
  }, []);

  const handleToggle = () => {
    if (darkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'false');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    }
    setDarkMode(!darkMode);
  };

  return (

    <SwitchField>
        <Switch name="change_darkmode" onClick={handleToggle} />
    </SwitchField>
  );
};

export default DarkModeToggle;
