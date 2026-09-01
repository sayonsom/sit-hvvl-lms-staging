import React from 'react';
import { InformationCircleIcon } from '@heroicons/react/24/solid'

const InfoIcon = ({ docUrl }) => {
  const redirectToDoc = () => {
    window.location.href = docUrl; // Redirect to documentation URL
  };

  return (
    // Using TailwindCSS for styling
    <span 
      className="inline-block cursor-pointer" 
      onClick={redirectToDoc} 
      role="button" 
      tabIndex="0" // For keyboard accessibility
      aria-label="Information" // Accessibility label
    >
        <InformationCircleIcon className="h-5 w-5" />
    </span>
  );
};

export default InfoIcon;
