import React from "react";
import { Link, useSearchParams } from "react-router-dom";

// Reasons the LTI backend can report when it refuses to issue a session.
// Provisioning failures are recoverable and must not be presented as an
// ordinary "no courses assigned" state.
const PROVISIONING_MESSAGES = {
  missing_email: "Your LMS launch did not include an email address, so your lab account could not be set up.",
  service_token_not_configured: "The lab service is not fully configured. This is a server-side setting, not a problem with your account.",
  backend_unreachable: "The lab could not reach the student records service. This is usually temporary.",
};

function provisioningMessage(reason) {
  if (PROVISIONING_MESSAGES[reason]) return PROVISIONING_MESSAGES[reason];
  if (reason && reason.startsWith("provision_http_")) {
    return "The student records service rejected the request to set up your account.";
  }
  return "Your lab account could not be set up during launch.";
}

export default function LtiRequired() {
  const [searchParams] = useSearchParams();
  const error = searchParams.get("error");
  const reason = searchParams.get("reason");
  const ref = searchParams.get("ref");

  if (error === "provisioning_failed") {
    return (
      <div style={{ padding: 24 }}>
        <h1>We could not finish setting up your lab account</h1>
        <p>{provisioningMessage(reason)}</p>
        <p>
          Please return to your LMS and relaunch the activity. If it happens
          again, contact support and quote the reference below.
        </p>
        {ref && (
          <p>
            Reference: <code>{ref}</code>
          </p>
        )}
        <Link to="/">Go to homepage</Link>
      </div>
    );
  }

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
