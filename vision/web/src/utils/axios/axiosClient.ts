import axios, { AxiosError, AxiosInstance, AxiosResponse } from "axios";
import axiosRetry from 'axios-retry';
import { store } from "../../redux/store";
import { setResponse } from "../../redux/slices/general";

//import { serverUrl } from '../../tools/urls';

const createAxiosInstance = (): AxiosInstance => {

  const instance = axios.create({
    baseURL: process.env.REACT_APP_SERVER_URL,
    headers: {
      "Content-Type": "multipart/form-data",
    },
    responseType: 'arraybuffer',
  });

  // interceptor to handle errors
  instance.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError) => {
      let response = {
        type: 'error',
        code: error.response?.status ? error.response?.status : 503,
        message: error.response?.statusText ? (error.response?.statusText + '.') : "Connection Refused." 
      }
      store.dispatch(setResponse(response));
      return Promise.reject(error);
    }
  );

  axiosRetry(instance, {
    retries: 3,
    retryDelay: (retryCount: number) => {
      console.log(`Retry attempt: ${retryCount}`);
      // waiting 2 seconds between each retry
      return 2000;
    },
    retryCondition: (error: any) => {
      // retrying only on 503 HTTP errors
      return error.response && error.response.status === 503;
    },
  });

  return instance;
};


export const axiosClient = createAxiosInstance();
