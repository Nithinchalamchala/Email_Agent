import { Configuration } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId:              process.env.REACT_APP_AZURE_CLIENT_ID!,
    authority:             `https://login.microsoftonline.com/${process.env.REACT_APP_AZURE_TENANT_ID}`,
    redirectUri:           process.env.REACT_APP_REDIRECT_URI ?? "http://localhost:3000",
    postLogoutRedirectUri: process.env.REACT_APP_REDIRECT_URI ?? "http://localhost:3000",
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

export const graphScopes = ["Mail.Read", "Mail.ReadWrite", "Calendars.ReadWrite"];
