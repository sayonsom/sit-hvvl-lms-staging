import {
  AAD_ALLOWED_EMAIL_DOMAIN,
  AAD_ALLOWED_EMAILS,
  AAD_ALLOWED_GROUP_IDS,
  AAD_ALLOWED_ROLES,
  AAD_AUTHORITY,
  AAD_CLIENT_ID,
  AAD_REDIRECT_URI,
  AAD_SCOPES,
  AAD_TENANT_ID,
} from "./env";

const DEFAULT_CLIENT_ID = "00000000-0000-0000-0000-000000000000";
const DEFAULT_AUTHORITY = "https://login.microsoftonline.com/organizations";

const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost";

const resolveAuthority = () => {
  if (AAD_AUTHORITY) return AAD_AUTHORITY;
  if (AAD_TENANT_ID) return `https://login.microsoftonline.com/${AAD_TENANT_ID}`;
  return DEFAULT_AUTHORITY;
};

const authority = resolveAuthority();

const getAuthorityHost = (value) => {
  try {
    return new URL(value).host;
  } catch {
    return undefined;
  }
};

const authorityHost = getAuthorityHost(authority);
const isMicrosoftOnlineAuthority = authorityHost
  ? authorityHost === "login.microsoftonline.com" || authorityHost.endsWith(".microsoftonline.com")
  : false;
const useCustomOidcAuthority = Boolean(authorityHost && !isMicrosoftOnlineAuthority);

const resolveRedirectUri = () => {
  if (!AAD_REDIRECT_URI) {
    return `${origin}/staff`;
  }

  if (AAD_REDIRECT_URI.startsWith("http://") || AAD_REDIRECT_URI.startsWith("https://")) {
    return AAD_REDIRECT_URI;
  }

  return `${origin}${AAD_REDIRECT_URI.startsWith("/") ? "" : "/"}${AAD_REDIRECT_URI}`;
};

const redirectUri = resolveRedirectUri();

export const isAadConfigured = Boolean(AAD_CLIENT_ID);

export const msalConfig = {
  auth: {
    clientId: AAD_CLIENT_ID || DEFAULT_CLIENT_ID,
    authority,
    ...(useCustomOidcAuthority
      ? {
          knownAuthorities: [authorityHost],
          protocolMode: "OIDC",
        }
      : {}),
    redirectUri,
    postLogoutRedirectUri: `${origin}/`,
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

const parseCsv = (value) =>
  typeof value === "string"
    ? value
        .split(",")
        .map((v) => v.trim())
        .filter(Boolean)
    : [];

export const aadRestrictions = {
  allowedEmailDomain: AAD_ALLOWED_EMAIL_DOMAIN || undefined,
  allowedEmails: parseCsv(AAD_ALLOWED_EMAILS).map((e) => e.toLowerCase()),
  allowedGroupIds: parseCsv(AAD_ALLOWED_GROUP_IDS),
  allowedRoles: parseCsv(AAD_ALLOWED_ROLES),
};

export const loginRequest = {
  scopes:
    parseCsv(AAD_SCOPES).length > 0
      ? parseCsv(AAD_SCOPES)
      : useCustomOidcAuthority
        ? ["openid"]
        : ["openid", "profile", "email"],
};
