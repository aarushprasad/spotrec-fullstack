export async function getRecommendations() {
  const response = await fetch("http://127.0.0.1:8000/api/me/recommendations", {
    credentials: "include",  // THIS sends cookies with the request
  });
  console.log(response)
  if (!response.ok) {
    console.log("Throwing error...")
    throw new Error("Oops, failed to fetch recommendations");
  }
  return response.json();
}

