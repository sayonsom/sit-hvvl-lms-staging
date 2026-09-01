const runtimeEnv =
  typeof window !== "undefined" && window.__ENV && typeof window.__ENV === "object"
    ? window.__ENV
    : {};

const buildEnv = import.meta.env || {};

const nonEmpty = (value) => {
  if (typeof value !== "string") return value;
  return value.trim() === "" ? undefined : value;
};

export const API_URL =
  nonEmpty(runtimeEnv.REACT_APP_API_URL) ??
  nonEmpty(buildEnv.REACT_APP_API_URL) ??
  nonEmpty(buildEnv.VITE_API_URL);
export const LTI_API_URL =
  nonEmpty(runtimeEnv.REACT_APP_LTI_API_URL) ??
  nonEmpty(buildEnv.REACT_APP_LTI_API_URL) ??
  nonEmpty(buildEnv.VITE_LTI_API_URL) ??
  (typeof window !== "undefined" ? window.location.origin : undefined);
export const MAPS_API =
  nonEmpty(runtimeEnv.REACT_APP_MAPS_API) ??
  nonEmpty(buildEnv.REACT_APP_MAPS_API) ??
  nonEmpty(buildEnv.VITE_MAPS_API);

// Azure AD (Microsoft Entra ID) - optional staff/admin direct login
export const AAD_CLIENT_ID =
  nonEmpty(runtimeEnv.REACT_APP_AAD_CLIENT_ID) ??
  nonEmpty(buildEnv.REACT_APP_AAD_CLIENT_ID) ??
  nonEmpty(buildEnv.VITE_AAD_CLIENT_ID);
export const AAD_TENANT_ID =
  nonEmpty(runtimeEnv.REACT_APP_AAD_TENANT_ID) ??
  nonEmpty(buildEnv.REACT_APP_AAD_TENANT_ID) ??
  nonEmpty(buildEnv.VITE_AAD_TENANT_ID);
export const AAD_AUTHORITY =
  nonEmpty(runtimeEnv.REACT_APP_AAD_AUTHORITY) ??
  nonEmpty(buildEnv.REACT_APP_AAD_AUTHORITY) ??
  nonEmpty(buildEnv.VITE_AAD_AUTHORITY);
export const AAD_REDIRECT_URI =
  nonEmpty(runtimeEnv.REACT_APP_AAD_REDIRECT_URI) ??
  nonEmpty(buildEnv.REACT_APP_AAD_REDIRECT_URI) ??
  nonEmpty(buildEnv.VITE_AAD_REDIRECT_URI);
export const AAD_SCOPES =
  nonEmpty(runtimeEnv.REACT_APP_AAD_SCOPES) ??
  nonEmpty(buildEnv.REACT_APP_AAD_SCOPES) ??
  nonEmpty(buildEnv.VITE_AAD_SCOPES);
export const AAD_ALLOWED_GROUP_IDS =
  nonEmpty(runtimeEnv.REACT_APP_AAD_ALLOWED_GROUP_IDS) ??
  nonEmpty(buildEnv.REACT_APP_AAD_ALLOWED_GROUP_IDS) ??
  nonEmpty(buildEnv.VITE_AAD_ALLOWED_GROUP_IDS);
export const AAD_ALLOWED_ROLES =
  nonEmpty(runtimeEnv.REACT_APP_AAD_ALLOWED_ROLES) ??
  nonEmpty(buildEnv.REACT_APP_AAD_ALLOWED_ROLES) ??
  nonEmpty(buildEnv.VITE_AAD_ALLOWED_ROLES);
export const AAD_ALLOWED_EMAIL_DOMAIN =
  nonEmpty(runtimeEnv.REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN) ??
  nonEmpty(buildEnv.REACT_APP_AAD_ALLOWED_EMAIL_DOMAIN) ??
  nonEmpty(buildEnv.VITE_AAD_ALLOWED_EMAIL_DOMAIN);
export const AAD_ALLOWED_EMAILS =
  nonEmpty(runtimeEnv.REACT_APP_AAD_ALLOWED_EMAILS) ??
  nonEmpty(buildEnv.REACT_APP_AAD_ALLOWED_EMAILS) ??
  nonEmpty(buildEnv.VITE_AAD_ALLOWED_EMAILS);
