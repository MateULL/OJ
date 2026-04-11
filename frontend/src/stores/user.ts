import { defineStore } from "pinia";
import {
  fetchMe,
  loginUser,
  logoutUser,
  registerUser,
  type AuthPayload,
  type MeResponse,
  type RegisterPayload
} from "../api/auth";

interface UserState {
  id: number | null;
  username: string;
  isAuthenticated: boolean;
  isDemo: boolean;
  loaded: boolean;
}

function applyUserPayload(state: UserState, payload: MeResponse) {
  state.id = payload.id;
  state.username = payload.username;
  state.isAuthenticated = payload.is_authenticated;
  state.isDemo = payload.is_demo;
}

export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    id: null,
    username: "",
    isAuthenticated: false,
    isDemo: false,
    loaded: false
  }),
  actions: {
    clear() {
      this.id = null;
      this.username = "";
      this.isAuthenticated = false;
      this.isDemo = false;
    },
    async loadMe() {
      try {
        const data = await fetchMe();
        applyUserPayload(this, data);
      } catch {
        this.clear();
      } finally {
        this.loaded = true;
      }
    },
    async ensureLoaded() {
      if (this.loaded) {
        return;
      }
      await this.loadMe();
    },
    async login(payload: AuthPayload) {
      const data = await loginUser(payload);
      applyUserPayload(this, data);
      this.loaded = true;
    },
    async register(payload: RegisterPayload) {
      const data = await registerUser(payload);
      applyUserPayload(this, data);
      this.loaded = true;
    },
    async logout() {
      await logoutUser();
      this.clear();
      this.loaded = true;
    }
  }
});
