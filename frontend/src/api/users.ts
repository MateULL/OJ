import { http } from "./http";

export interface CheckinValue {
  date: string;
  count: number;
}

export interface CheckinStats {
  total_active_days: number;
  year_active_days: number;
  last_30_days_active_days: number;
  max_streak_days: number;
}

export interface CheckinResponse {
  month?: string;
  year?: string;
  active_days?: number;
  available_years?: number[];
  stats?: CheckinStats;
  values: CheckinValue[];
}

export interface CheckinQuery {
  month?: string;
  year?: string | number;
}

export async function fetchCheckins(params: CheckinQuery): Promise<CheckinResponse> {
  const response = await http.get<CheckinResponse>("/users/me/checkins/", {
    params
  });
  return response.data;
}
