// src/api/adminAxios.js
import axios from 'axios';

export const adminAxios = axios.create({
  baseURL: process.env.REACT_APP_BASE_URL,
 
});


export const WebsocketAxios = process.env.REACT_APP_WS_BASE_URL;



