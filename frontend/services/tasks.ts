import axios from "axios";

// TypeScript interface matching the Redis telemetry shape from your FastAPI backend
export interface TaskTelemetry {
    task_id: string;
    status: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE";
    result: any;
    traceback: string | null;
}

/**
 * Queries the Redis result backend via Nginx proxy to fetch live task execution telemetry.
 */
export async function getTaskStatus(taskId: string): Promise<TaskTelemetry> {
    // 🚀 Relative routing maps straight to http://164.68.120.179/api/tasks/[id] via Nginx
    const response = await axios.get(`/api/tasks/${taskId}`);
    return response.data;
}