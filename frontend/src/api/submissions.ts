import { http } from "./http";

export type SubmissionStatus = "QUEUED" | "JUDGING" | "FINISHED";
export type Verdict = "AC" | "WA" | "CE" | "RE" | "TLE" | "MLE" | "OLE" | "SE" | null;

export interface CaseResult {
  id: number;
  test_case: number;
  test_case_order: number;
  verdict: Exclude<Verdict, null>;
  time_used_ms: number;
  memory_used_kb: number;
  message: string;
  created_at: string;
}

export interface Submission {
  id: number;
  problem: number;
  problem_title: string;
  username: string;
  language: string;
  source_code?: string;
  status: SubmissionStatus;
  final_verdict: Verdict;
  total_time_ms: number;
  max_memory_kb: number;
  compile_log?: string;
  submitted_at: string;
  judged_at: string | null;
  case_results?: CaseResult[];
}

export interface CreateSubmissionPayload {
  problem: number;
  language: string;
  source_code: string;
}

export async function fetchSubmissions(problem?: number): Promise<Submission[]> {
  const response = await http.get<Submission[]>("/submissions/", {
    params: problem ? { problem } : undefined
  });
  return response.data;
}

export async function fetchSubmission(id: number): Promise<Submission> {
  const response = await http.get<Submission>(`/submissions/${id}/`);
  return response.data;
}

export async function createSubmission(payload: CreateSubmissionPayload): Promise<Submission> {
  const response = await http.post<Submission>("/submissions/", payload);
  return response.data;
}
