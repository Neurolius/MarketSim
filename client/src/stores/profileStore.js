import { defineStore } from "pinia";
import { ref, onBeforeMount } from "vue";
import axios from "axios";
import Cookies from "js-cookie";

const useProfileStore = defineStore("profileStore", () => {
  const isAuthenticated = ref(false);
  const userName = ref(null);
  const isLoaded = ref(false);

  async function fetchMe() {
    const r = await axios.get("/api/profile/me/");
    axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");
    isAuthenticated.value = r.data.is_authenticated;
    userName.value = r.data.is_authenticated ? r.data.username : null;
    isLoaded.value = true;
  }

  async function login(username, password) {
    try {
      const r = await axios.post("/api/profile/login/", {
        username: username,
        password: password,
      });
      await fetchMe();
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || "Неверный юзернейм или пароль";
      throw new Error(errorMessage);
    }
  }

  async function logout() {
    await axios.post("/api/profile/logout/");
    await fetchMe();
  }

  onBeforeMount(() => {
    fetchMe();
  });

  return {
    isAuthenticated,
    userName,
    fetchMe,
    login,
    logout,
  };
});

export default useProfileStore;
