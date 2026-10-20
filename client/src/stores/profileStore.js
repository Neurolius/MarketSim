import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";
import Cookies from "js-cookie";

const useProfileStore = defineStore("profileStore", () => {
  const isAuthenticated = ref(false);
  const userName = ref(null);
  const userId = ref(null);
  const isSuperuser = ref(false);
  const isLoaded = ref(false);

  async function fetchMe() {
    try {
      const r = await axios.get("/api/profile/me/");
      axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");
      isAuthenticated.value = r.data.is_authenticated;
      userName.value = r.data.username ?? null;
      userId.value = r.data.id ?? null;
      isSuperuser.value = !!r.data.is_superuser;
    } catch (e) {
      console.error("Error ", e);
      isAuthenticated.value = false;
      userName.value = null;
      userId.value = null;
      isSuperuser.value = false;
    } finally {
      isLoaded.value = true;
    }
  }

  async function login(username, password) {
    await axios.post("/api/profile/login/", { username, password });
    await fetchMe();
  }

  async function logout() {
    await axios.post("/api/profile/logout/");
    await fetchMe();
  }

  async function register(username, password) {
    await axios.post("/api/profile/register/", { username, password });
    await fetchMe();
  }

  return {
    isAuthenticated,
    userName,
    userId,
    isSuperuser,
    isLoaded,
    fetchMe,
    login,
    logout,
    register,
  };
});

export default useProfileStore;
