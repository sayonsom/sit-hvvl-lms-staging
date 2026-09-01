import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { aadRestrictions, isAadConfigured } from "../authConfig";
import { useLTI } from "../contexts/LTIContext";
import { LTI_API_URL } from "../env";

const normalizeDomain = (domain) => {
  if (typeof domain !== "string") return undefined;
  const trimmed = domain.trim();
  if (!trimmed) return undefined;
  return trimmed.startsWith("@") ? trimmed.slice(1) : trimmed;
};

const toArray = (value) => {
  if (Array.isArray(value)) return value;
  if (typeof value === "string" && value.trim() !== "") return [value.trim()];
  return [];
};

const isAccountAllowed = (claims, email = "") => {
  const accountEmail = email || claims?.email || claims?.upn || claims?.unique_name || "";

  const allowedEmails = aadRestrictions.allowedEmails || [];
  if (allowedEmails.length > 0 && !allowedEmails.includes(accountEmail.toLowerCase())) {
    return { allowed: false, reason: "Your account is not in the allowed staff list." };
  }

  const allowedDomain = normalizeDomain(aadRestrictions.allowedEmailDomain);
  if (allowedDomain && !accountEmail.toLowerCase().endsWith(`@${allowedDomain.toLowerCase()}`)) {
    return { allowed: false, reason: `Email domain must be @${allowedDomain}.` };
  }

  const allowedGroupIds = aadRestrictions.allowedGroupIds || [];
  const tokenGroups = toArray(claims.groups);
  if (allowedGroupIds.length > 0 && !tokenGroups.some((g) => allowedGroupIds.includes(g))) {
    return { allowed: false, reason: "Your account is not in an allowed staff/admin group." };
  }

  const allowedRoles = aadRestrictions.allowedRoles || [];
  const tokenRoles = toArray(claims.roles);
  if (allowedRoles.length > 0 && !tokenRoles.some((r) => allowedRoles.includes(r))) {
    return { allowed: false, reason: "Your account does not have an allowed staff/admin role." };
  }

  return { allowed: true };
};

const getValue = (query, hash, key) => query.get(key) || hash.get(key);

const buildLtiUrl = (path) => {
  const base = (LTI_API_URL || "").replace(/\/$/, "");
  if (!base) return path;
  if (base.startsWith("http://") || base.startsWith("https://")) return `${base}${path}`;
  if (base.startsWith("/")) return `${base}${path}`;
  return `${window.location.origin}/${base}${path}`;
};

export default function StaffEntry() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginStaff, logout } = useLTI();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const callbackHandled = useRef(false);

  const callbackData = useMemo(() => {
    const query = new URLSearchParams(location.search);
    const hash = new URLSearchParams(location.hash.startsWith("#") ? location.hash.slice(1) : "");
    return {
      code: getValue(query, hash, "code"),
      state: getValue(query, hash, "state"),
      errorCode: getValue(query, hash, "error"),
      errorDescription: getValue(query, hash, "error_description"),
      requestId:
        getValue(query, hash, "client-request-id") || getValue(query, hash, "client_request_id"),
    };
  }, [location.hash, location.search]);

  useEffect(() => {
    const { code, state, errorCode, errorDescription, requestId } = callbackData;
    const hasValidAuthCodePayload = Boolean(code && state);
    const shouldShowProviderError = Boolean(
      errorCode || errorDescription || (requestId && !hasValidAuthCodePayload)
    );

    if (!shouldShowProviderError) return;

    const parts = [];
    if (errorCode) parts.push(`Sign-in failed (${errorCode}).`);
    if (errorDescription) parts.push(errorDescription);
    if (!errorCode && !errorDescription && requestId) {
      parts.push("Sign-in failed at identity provider.");
    }
    if (requestId) parts.push(`Request ID: ${requestId}`);

    setError(parts.join(" "));
  }, [callbackData]);

  useEffect(() => {
    if (!isAadConfigured) return;
    if (location.pathname !== "/oauth2/callback") return;
    if (callbackHandled.current) return;

    const { code, state, errorCode, errorDescription } = callbackData;
    if (errorCode || errorDescription) return;
    if (!code || !state) return;

    callbackHandled.current = true;
    setIsLoading(true);
    setError(null);

    const exchangeCode = async () => {
      try {
        const response = await axios.post(
          buildLtiUrl("/lti/staff/exchange"),
          { code, state },
          { timeout: 20000 }
        );

        const user = response?.data?.user || null;
        const claims = response?.data?.claims || {};
        if (!user) {
          setError("Staff sign-in response is missing user data.");
          return;
        }

        const { allowed, reason } = isAccountAllowed(claims, user.email || "");
        if (!allowed) {
          setError(reason || "Access denied.");
          return;
        }

        loginStaff(
          {
            email: user.email || "",
            name: user.name || user.email || "Staff User",
            picture:
              user.picture ||
              `https://ui-avatars.com/api/?name=${encodeURIComponent(
                user.name || user.email || "Staff User"
              )}&size=200`,
            user_id: user.user_id || user.email || user.sub || "staff",
          },
          response?.data?.api_token
        );

        navigate("/home", { replace: true });
      } catch (e) {
        const detail =
          e?.response?.data?.detail ||
          e?.message ||
          "Sign-in failed while exchanging the authorization code.";
        setError(String(detail));
      } finally {
        setIsLoading(false);
      }
    };

    exchangeCode();
  }, [callbackData, location.pathname, loginStaff, navigate]);

  const handleSignIn = () => {
    setError(null);
    if (!isAadConfigured) {
      setError("Staff/Admin sign-in is not configured. Set REACT_APP_AAD_CLIENT_ID.");
      return;
    }
    const shouldForceReauth = localStorage.getItem("staff_force_reauth") === "1";
    const loginPath = shouldForceReauth
      ? "/lti/staff/login?prompt=login"
      : "/lti/staff/login";
    window.location.assign(buildLtiUrl(loginPath));
  };

  const handleSignOut = async () => {
    setError(null);
    try {
      await logout();
    } catch (e) {
      console.error("Logout error:", e);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 px-6">
      <div className="w-full max-w-lg rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-heading font-bold text-gray-900">Staff / Admin Access</h1>
        <p className="mt-2 text-sm text-gray-600">
          Sign in with SIT Active Directory (Microsoft Entra ID) to access the lab directly (without a
          Brightspace launch).
        </p>

        {!isAadConfigured ? (
          <div className="mt-4 rounded-md bg-yellow-50 p-4 text-sm text-yellow-800">
            Staff sign-in is not configured for this environment.
          </div>
        ) : null}

        {error ? (
          <div className="mt-4 rounded-md bg-red-50 p-4 text-sm text-red-800">{error}</div>
        ) : null}

        <div className="mt-6 flex flex-col gap-3">
          <button
            type="button"
            onClick={handleSignIn}
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign in with Microsoft"}
          </button>

          <button
            type="button"
            onClick={handleSignOut}
            className="w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            disabled={isLoading}
          >
            Sign out
          </button>
        </div>

        <p className="mt-6 text-xs text-gray-500">
          Students should launch from Brightspace. If you’re a staff user and you see access denied,
          ask SIT to add your account to the configured staff/admin group/role for this tool.
        </p>
      </div>
    </div>
  );
}
