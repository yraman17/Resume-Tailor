export default function TagList({ title, items = [], hint }) {
    return (
      <div style={{padding:16, border:"1px solid #e5e7eb", borderRadius:12}}>
        <div style={{display:"flex", justifyContent:"space-between", alignItems:"baseline"}}>
          <h3 style={{margin:"0 0 8px 0"}}>{title}</h3>
          {hint && <span style={{color:"#6b7280", fontSize:12}}>{hint}</span>}
        </div>
        {items.length === 0 ? (
          <div style={{color:"#6b7280", fontStyle:"italic"}}>None</div>
        ) : (
          <div style={{display:"flex", flexWrap:"wrap", gap:8}}>
            {items.map((x, i) => (
              <span key={i} style={{
                padding:"6px 10px", background:"#f3f4f6", borderRadius:999, fontSize:14
              }}>{x}</span>
            ))}
          </div>
        )}
      </div>
    );
  }
  