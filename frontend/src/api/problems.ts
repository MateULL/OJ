import { http } from "./http";

export interface Problem {
  id: number;
  title: string;
  description?: string;
  sample_input?: string;
  sample_output?: string;
  time_limit_ms: number;
  memory_limit_mb: number;
  judge_mode: string;
  is_public: boolean;
}

export async function fetchProblems(query = ""): Promise<Problem[]> {
  const response = await http.get<Problem[]>("/problems/", {
    params: query ? { q: query } : undefined
  });
  return response.data;
}

export async function fetchProblem(id: number): Promise<Problem> {
  const response = await http.get<Problem>(`/problems/${id}/`);
  return response.data;
}
