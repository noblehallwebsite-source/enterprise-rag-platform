// src/services/api.ts
import axios from "axios";

export const api = axios.create({
    baseURL: "/api", // 🔥 ALWAYS go through Next.js API routes
});