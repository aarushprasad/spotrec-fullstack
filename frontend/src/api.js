const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export async function getRecommendations() {
  const response = await fetch(`${BACKEND_URL}/api/me/recommendations`, {
    credentials: "include",  // THIS sends cookies with the request
  });
  console.log(response)
  if (!response.ok) {
    console.log("Throwing error...")
    throw new Error("Oops, failed to fetch recommendations");
  }
  return response.json();
}

