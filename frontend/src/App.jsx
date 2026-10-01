import { useEffect, useState } from "react";

export default function App() {
  const [users, setUsers] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  async function loadUsers() {
    const response = await fetch("/api/users");
    if (!response.ok) throw new Error("Could not load users");
    setUsers(await response.json());
  }

  useEffect(() => {
    loadUsers().catch((error) => setMessage(error.message));
  }, []);

  async function addUser(event) {
    event.preventDefault();
    setMessage("");
    try {
      const response = await fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not create user");
      setName("");
      setEmail("");
      setMessage("User created successfully");
      await loadUsers();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main className="container">
      <h1>User Management</h1>
      <p className="subtitle">React + FastAPI + MySQL on Kubernetes</p>
      <form onSubmit={addUser}>
        <input value={name} onChange={(e) => setName(e.target.value)}
          placeholder="Full name" required maxLength="120" />
        <input type="email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email address" required />
        <button type="submit">Add user</button>
      </form>
      {message && <p className="message">{message}</p>}
      <h2>Users ({users.length})</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id}><strong>{user.name}</strong><span>{user.email}</span></li>
        ))}
      </ul>
    </main>
  );
}
