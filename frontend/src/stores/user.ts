import { defineStore } from "pinia";
import { http } from "../api/http";

interface UserState {
  id: number | null;
  username: string;
  isAuthenticated: boolean;
  isDemo: boolean;
}

export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    id: null,
    username: "",
    isAuthenticated: false,
    isDemo: true
  }),
  actions: {
    async loadMe() {
      const response = await http.get<{
        id: number;
        username: string;
        is_authenticated: boolean;
        is_demo: boolean;
      }>("/users/me/");

      this.id = response.data.id;
      this.username = response.data.username;
      this.isAuthenticated = response.data.is_authenticated;
      this.isDemo = response.data.is_demo;
    }
  }
});
