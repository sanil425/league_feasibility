export async function simulateLeague(userPrompt) {
    console.log("Calling API with:", userPrompt);

    const endpoint = "/simulate";  // ✅ Absolute fix: Always use relative path

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