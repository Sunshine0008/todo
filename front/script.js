// 1. Load tasks from the Database when the page opens
document.addEventListener('DOMContentLoaded', async () => {
    const userId = localStorage.getItem('userId'); // Retrieve the logged-in user's ID
    if (!userId) return;

    // Notice the /${userId} added to the URL
    const response = await fetch(`${API_URL}/${userId}`); 
    const tasks = await response.json();
    tasks.forEach(task => renderTask(task));
});

// 2. Update createNewTask to send the userId
async function createNewTask() {
    const input = document.getElementById('taskInput');
    const taskValue = input.value.trim();
    if (taskValue === "") return;

    const vibes = ["✨ ", "🔥 ", "💀 ", "🤡 ", "🚀 "];
    const randomVibe = vibes[Math.floor(Math.random() * vibes.length)];
    const fullText = randomVibe + taskValue;
    const userId = localStorage.getItem('userId');

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            text: fullText,
            user_id: parseInt(userId) // FastAPI expects an integer
        })
    });

    const newTask = await response.json();
    renderTask(newTask);
    input.value = "";
}
