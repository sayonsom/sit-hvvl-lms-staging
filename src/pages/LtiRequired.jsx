import React from "react";
import { Link } from "react-router-dom";

export default function LtiRequired() {
  return (
    <div style={{ padding: 24 }}>
      <h1>LTI Session Required</h1>
      <p>
        This page must be launched with a valid LTI session. Please return to
        your LMS and relaunch the activity.
      </p>
      <p>
        If you believe this is an error, contact support or go back to the
        homepage.
      </p>
      <Link to="/">Go to homepage</Link>
    </div>
  );
}

