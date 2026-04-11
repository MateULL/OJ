import { http } from "./http";

export interface CheckinValue {
  date: string;
  count: number;
}

export interface CheckinResponse {
  month: string;
  active_days: number;
  values: CheckinValue[];
}

export async function fetchCheckins(month: string): Promise<CheckinResponse> {
  const response = await http.get<CheckinResponse>("/users/me/checkins/", {
    params: { month }
  });
  return response.data;
}
