export async function simulateLeague(userPrompt) {
    console.log("Calling API with:", userPrompt);

    // Use .env variable if available, fallback to localhost for dev
    const baseURL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";
    const endpoint = `${baseURL}/simulate/`;

    const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_prompt: userPrompt })  // ✅ must use "user_prompt"
    });

    if (!response.ok) {
        throw new Error("Error simulating league");
    }

    return await response.json();
}
