import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL, LTI_API_URL } from "../env";

const LTIContext = createContext();
const API_TOKEN_KEY = 'vhvl_api_token';

const setDefaultAuthHeader = (token) => {
  if (token) {
    axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common.Authorization;
  }
};

const resolveLtiUrl = (path) => {
  const base = (LTI_API_URL || "").replace(/\/$/, "");
  if (!base) return path;
  if (base.startsWith("http://") || base.startsWith("https://")) return `${base}${path}`;
  if (base.startsWith("/")) return `${base}${path}`;
  if (typeof window !== "undefined") return `${window.location.origin}/${base}${path}`;
  return `${base}${path}`;
};

const clearStoredAuth = () => {
  sessionStorage.removeItem('lti_session_token');
  sessionStorage.removeItem('lti_user');
  sessionStorage.removeItem('lti_course');
  sessionStorage.removeItem(API_TOKEN_KEY);
  sessionStorage.removeItem('staff_user');
  setDefaultAuthHeader(null);
};

const validateApiToken = async (apiToken) => {
  if (!apiToken || !API_URL) return null;
  const response = await axios.get(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${apiToken}` },
    timeout: 10000,
  });
  return response.data;
};

export const LTIProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [course, setCourse] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authMethod, setAuthMethod] = useState("none"); // lti | staff | none

  useEffect(() => {
    // Check for session token in tab-scoped storage
    const validateSession = async () => {
      const sessionToken = sessionStorage.getItem('lti_session_token');

      if (sessionToken) {
        // An LTI session always wins over a stale staff_user cache — clear
        // it up front so an in-flight validate can't race with a leftover
        // instructor identity.
        sessionStorage.removeItem('staff_user');
        try {
          const response = await axios.get(
            `${LTI_API_URL}/lti/session/validate`,
            {
              headers: { Authorization: `Bearer ${sessionToken}` },
              timeout: 10000
            }
          );

          const apiToken = response.data.api_token;
          if (!apiToken) {
            throw new Error('Session validation response is missing API token');
          }
          sessionStorage.setItem(API_TOKEN_KEY, apiToken);
          setDefaultAuthHeader(apiToken);
          
          setUser(response.data.user);
          setCourse(response.data.course);
          setIsAuthenticated(true);
          setAuthMethod("lti");
          
          console.log('Session validated:', {
            user: response.data.user.email,
            course: response.data.course.course_title
          });
        } catch (error) {
          console.error('Session validation failed:', error);
          // Clear invalid session
          clearStoredAuth();
          setIsAuthenticated(false);
          setUser(null);
          setCourse(null);
          setAuthMethod("none");
        }
      } else {
        const staffUserJson = sessionStorage.getItem('staff_user');
        const apiToken = sessionStorage.getItem(API_TOKEN_KEY);
        if (staffUserJson && apiToken) {
          try {
            const actor = await validateApiToken(apiToken);
            const roles = Array.isArray(actor?.roles) ? actor.roles : [];
            if (!roles.some((role) => ["teacher", "admin", "service"].includes(role))) {
              throw new Error('Stored staff token is not authorized for staff access');
            }
            const staffUser = JSON.parse(staffUserJson);
            setDefaultAuthHeader(apiToken);
            setUser(staffUser);
            setCourse(null);
            setIsAuthenticated(true);
            setAuthMethod("staff");
            setIsLoading(false);
            return;
          } catch (e) {
            console.error('Error validating staff session:', e);
            clearStoredAuth();
          }
        }

        const cachedUser = sessionStorage.getItem('lti_user');
        const cachedCourse = sessionStorage.getItem('lti_course');
        
        if (!isAuthenticated && cachedUser && cachedCourse && apiToken) {
          try {
            await validateApiToken(apiToken);
            setDefaultAuthHeader(apiToken);
            setUser(JSON.parse(cachedUser));
            setCourse(JSON.parse(cachedCourse));
            setIsAuthenticated(true);
            setAuthMethod("lti");
          } catch (e) {
            console.error('Error parsing cached data:', e);
          }
        }
      }
      
      setIsLoading(false);
    };

    validateSession();
    
    // Optional: Set up session refresh interval (every 30 minutes)
    const refreshInterval = setInterval(() => {
      const sessionToken = sessionStorage.getItem('lti_session_token');
      if (sessionToken) {
        axios.get(
          `${LTI_API_URL}/lti/session/refresh`,
          { headers: { Authorization: `Bearer ${sessionToken}` } }
        ).catch(err => {
          console.error('Session refresh failed:', err);
        });
      }
    }, 30 * 60 * 1000); // 30 minutes

    return () => clearInterval(refreshInterval);
  }, []);

  const loginStaff = (staffUser, apiToken) => {
    if (!apiToken) {
      throw new Error('Staff sign-in response is missing API token');
    }
    sessionStorage.setItem('staff_user', JSON.stringify(staffUser));
    sessionStorage.setItem(API_TOKEN_KEY, apiToken);
    localStorage.removeItem('staff_force_reauth');
    setDefaultAuthHeader(apiToken);
    setUser(staffUser);
    setCourse(null);
    setIsAuthenticated(true);
    setAuthMethod("staff");
  };

  const logout = async () => {
    const sessionToken = sessionStorage.getItem('lti_session_token');
    const hadLtiSession = Boolean(sessionToken);
    const hadStaffSession = Boolean(sessionStorage.getItem('staff_user'));

    if (sessionToken) {
      try {
        await axios.post(
          `${LTI_API_URL}/lti/logout`,
          {},
          {
            headers: { Authorization: `Bearer ${sessionToken}` },
            timeout: 5000
          }
        );
      } catch (error) {
        console.error('Logout error:', error);
        // Continue with logout even if API call fails
      }
    }

    // Preserve cross-session UI prefs that aren't tied to identity.
    const darkMode = localStorage.getItem('darkMode');

    // Nuke all per-tab session state (LTI token, cached user/course,
    // legacy HVLABuserEmail/StudentID, staff_user, anything else).
    sessionStorage.clear();

    // Clear any identity-related localStorage entries. Anything that
    // could re-hydrate a stale account must go here.
    localStorage.removeItem('staff_force_reauth');

    // Restore preserved UI prefs.
    if (darkMode !== null) {
      localStorage.setItem('darkMode', darkMode);
    }

    setDefaultAuthHeader(null);
    setUser(null);
    setCourse(null);
    setIsAuthenticated(false);
    setAuthMethod("none");

    // Redirect based on previous auth method. Each branch is a hard
    // navigation, which fully tears down React state — no chance for a
    // stale user to flash before the redirect lands.
    if (hadStaffSession) {
      localStorage.setItem('staff_force_reauth', '1');
      window.location.replace(resolveLtiUrl('/lti/staff/logout'));
      return;
    }
    if (hadLtiSession) {
      window.location.replace('/lti-required');
      return;
    }
    window.location.replace('/');
  };

  const updateUser = (userData) => {
    setUser(userData);
    sessionStorage.setItem('lti_user', JSON.stringify(userData));
  };

  const updateCourse = (courseData) => {
    setCourse(courseData);
    sessionStorage.setItem('lti_course', JSON.stringify(courseData));
  };

  return (
    <LTIContext.Provider
      value={{
        isAuthenticated,
        user,
        course,
        authMethod,
        isLoading,
        logout,
        loginStaff,
        updateUser,
        updateCourse,
      }}
    >
      {children}
    </LTIContext.Provider>
  );
};

export const useLTI = () => {
  const context = useContext(LTIContext);
  if (!context) {
    throw new Error('useLTI must be used within LTIProvider');
  }
  return context;
};

export default LTIContext;
