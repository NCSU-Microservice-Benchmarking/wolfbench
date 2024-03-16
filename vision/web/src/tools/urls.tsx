export const serverUrl = (process.env.NODE_ENV === 'production') 
? process.env.REACT_APP_SERVER_URL
: 'http://localhost:8080';

export const hostUrl = (process.env.NODE_ENV === 'production') 
? process.env.REACT_APP_CLIENT_URL
: "http://localhost:3000";