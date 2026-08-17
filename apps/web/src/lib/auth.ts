/**
 * Utility helper to ensure a valid JWT authentication token is present in localStorage.
 * If no token is present, it attempts to register or login a default demo account automatically.
 */
export async function getOrFetchAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  let token = localStorage.getItem("token");
  if (token) return token;

  const demoEmail = "demo@enterprise.com";
  const demoPassword = "DemoPassword123!";
  const demoOrg = "Enterprise Demo Inc";

  // Try logging in first
  try {
    const loginRes = await fetch("http://localhost:8000/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: demoEmail,
        password: demoPassword,
      }),
    });

    if (loginRes.ok) {
      const data = await loginRes.json();
      token = data.access_token;
      if (token) {
        localStorage.setItem("token", token);
        return token;
      }
    }
  } catch (err) {
    console.warn("Auto login error, attempting registration fallback:", err);
  }

  // If login failed (user doesn't exist yet), register default demo account
  try {
    const regRes = await fetch("http://localhost:8000/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: demoEmail,
        password: demoPassword,
        organization_name: demoOrg,
      }),
    });

    if (regRes.ok || regRes.status === 400) {
      // User registered (or already existed), now perform login
      const loginRes = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          username: demoEmail,
          password: demoPassword,
        }),
      });

      if (loginRes.ok) {
        const data = await loginRes.json();
        token = data.access_token;
        if (token) {
          localStorage.setItem("token", token);
          return token;
        }
      }
    }
  } catch (err) {
    console.error("Auto authentication failed:", err);
  }

  return null;
}
