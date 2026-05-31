// src/services/api.ts
import axios from "axios";

export const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: {
        "x-api-key": process.env.NEXT_PUBLIC_TENANT_API_KEY,
    },
});