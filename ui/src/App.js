import { useEffect, useState } from "react";

function App() {
  const [events, setEvents] = useState([]);

  const fetchEvents = async () => {
    const res = await fetch("http://localhost:5000/webhook/events");
    const data = await res.json();
    setEvents(data.events);
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 15000);
    return () => clearInterval(interval);
  }, []);

  const formatEvent = (e) => {
    const time = new Date(e.timestamp).toUTCString();

    if (e.action === "PUSH") {
      return `${e.author} pushed to ${e.to_branch} on ${time}`;
    }
    if (e.action === "PULL_REQUEST") {
      return `${e.author} submitted a pull request from ${e.from_branch} to ${e.to_branch} on ${time}`;
    }
    if (e.action === "MERGE") {
      return `${e.author} merged branch ${e.from_branch} to ${e.to_branch} on ${time}`;
    }
    return "";
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>GitHub Repository Activity</h2>
      {events.map((e, i) => (
        <div key={i} style={{
          background: "#fff",
          marginBottom: 10,
          padding: 12,
          borderRadius: 6
        }}>
          {formatEvent(e)}
        </div>
      ))}
    </div>
  );
}

export default App;
