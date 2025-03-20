import { useState, useEffect } from "react";

export default function SymlinkCleanerUI() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    setLoading(true);
    const res = await fetch("/api/status");
    const data = await res.json();
    setStatus(data);
    setLoading(false);
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>Symlink Cleaner Dashboard</h1>
      <p>Symlink Directory: {status.symlink_dir}</p>
      <p>Zurg Mount: {status.zurg_mount}</p>
    </div>
  );
}