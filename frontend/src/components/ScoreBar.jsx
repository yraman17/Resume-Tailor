export default function ScoreBar({ value = 0 }) {
    const pct = Math.max(0, Math.min(100, value));
    return (
      <div style={{background:"#eee", borderRadius:12, height:14, overflow:"hidden"}}>
        <div style={{
          width: `${pct}%`,
          height:"100%",
          background: pct >= 70 ? "#22c55e" : pct >= 40 ? "#f59e0b" : "#ef4444",
          transition:"width .35s ease"
        }}/>
      </div>
    );
  }
  