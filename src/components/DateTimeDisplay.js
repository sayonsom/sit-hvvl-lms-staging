import React, { useState, useEffect } from 'react';

const DateTimeDisplay = () => {
    const [currentDateTime, setCurrentDateTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentDateTime(new Date());
        }, 1000);

        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    // Format the date and time
    const formattedDateTime = currentDateTime.toLocaleString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric'
    });

    return (
        <h2 className="text-xl font-bold text-gray-900">{formattedDateTime}</h2>
    );
};

export default DateTimeDisplay;
