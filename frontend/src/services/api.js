// frontend/src/services/api.js

export async function simulateLeague(userPrompt) {
    console.log("Calling API with:", userPrompt);

    // Use environment variable or fallback to local dev
    const baseURL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";
    const endpoint = `${baseURL}/simulate/`;

    const response = await fetch(endpoint, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userPrompt })
    });

    if (!response.ok) {
        throw new Error("Error simulating league");
    }

    return await response.json();
}
