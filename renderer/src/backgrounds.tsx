import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

// ─── Photo backgrounds (real photos when available) ────────────────────────
const PHOTO_SCENES = new Set([
  "home", "kitchen", "bedroom", "park", "school", "shop", "street",
  "office", "library",
]);

// Scenes without their own photo borrow the closest real location
const PHOTO_ALIAS: Record<string, string> = {
  bathroom: "bedroom",
  notebook: "office",
  desk: "office",
  pencilcase: "shop",
  living_room: "home",
};

export const photoForScene = (label: string): string | null => {
  if (PHOTO_SCENES.has(label)) return label;
  return PHOTO_ALIAS[label] ?? null;
};

// Hand-tuned ground line per photo (portrait 1080x1920): px from frame bottom
// where characters' feet touch a believable surface in that image.
const PHOTO_GROUND: Record<string, number> = {
  kitchen: 470,  // countertop surface
  home:    200,  // wood floor
  park:    160,  // gravel path
  school:  260,  // classroom floor
  office:  220,  // corridor floor
  street:  200,  // asphalt
  bedroom: 180,  // carpet
  library: 200,  // in front of bottom shelves
  shop:    240,  // cafe floor
};

export const photoGroundBottom = (label: string): number | null => {
  const photo = photoForScene(label);
  return photo ? (PHOTO_GROUND[photo] ?? 270) : null;
};

// Deterministic per-scene pan direction so cuts back to a scene look consistent
const sceneHash = (label: string) => {
  let h = 0;
  for (let i = 0; i < label.length; i++) h = (h * 31 + label.charCodeAt(i)) & 0xffff;
  return h;
};

const PhotoBg: React.FC<{ label: string }> = ({ label }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const h = sceneHash(label);

  // Ken Burns: slow continuous push-in + drift, direction fixed per scene
  const t = frame / fps;
  const zoom = 1.10 + Math.sin(t * 0.045 + h) * 0.025;
  const panX = Math.sin(t * 0.060 + h * 0.7) * 18 * ((h % 2) ? 1 : -1);
  const panY = Math.cos(t * 0.050 + h * 1.3) * 12;

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={staticFile(`backgrounds/photos/${label}.jpg`)}
        style={{
          width: "100%", height: "100%", objectFit: "cover", objectPosition: "center 30%",
          transform: `scale(${zoom}) translate(${panX}px, ${panY}px)`,
          filter: "saturate(1.06) contrast(1.03)",
        }}
      />
      {/* darken so characters & text stay readable */}
      <div style={{ position: "absolute", inset: 0,
        background: "linear-gradient(180deg, rgba(0,0,0,0.16) 0%, rgba(0,0,0,0.06) 50%, rgba(0,0,0,0.30) 100%)" }} />
    </AbsoluteFill>
  );
};

// ─── Home / Living Room ────────────────────────────────────────────────────
const Home: React.FC = () => (
  <AbsoluteFill>
    {/* warm coral-orange wall */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"67%",
      background:"linear-gradient(180deg,#FF9966 0%,#FF7744 50%,#FF6633 100%)" }} />
    {/* wainscoting panel stripe */}
    <div style={{ position:"absolute", top:"54%", left:0, right:0, height:"14%",
      background:"#FF5522", borderTop:"6px solid #CC3300", borderBottom:"6px solid #CC3300" }} />
    {/* warm wood floor */}
    <div style={{ position:"absolute", top:"67%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#C8864A,#A06030)" }} />
    {[15,30,45,60,75].map(x=>(<div key={x} style={{ position:"absolute", top:"67%", bottom:0,
      left:`${x}%`, width:3, background:"rgba(0,0,0,0.12)" }} />))}
    {/* big blue window with curtains */}
    <div style={{ position:"absolute", top:"5%", left:"8%", width:"28%", height:"36%",
      background:"linear-gradient(180deg,#5BC8F5,#87DDFF)", border:"10px solid #FFF8EC",
      borderRadius:6, boxShadow:"0 6px 24px rgba(0,0,0,0.25)" }}>
      <div style={{ position:"absolute", top:0, bottom:0, left:"50%", width:5, background:"rgba(255,248,236,0.7)" }} />
      <div style={{ position:"absolute", left:0, right:0, top:"44%", height:5, background:"rgba(255,248,236,0.7)" }} />
      <div style={{ position:"absolute", top:"12%", right:"18%", width:22, height:22,
        borderRadius:"50%", background:"#FFE040", boxShadow:"0 0 20px #FFE040" }} />
    </div>
    {/* left curtain */}
    <div style={{ position:"absolute", top:"4%", left:"4%", width:"10%", height:"40%",
      background:"linear-gradient(180deg,#E83030,#C02020)",
      borderRadius:"6px 6px 40% 0" }} />
    {/* right curtain */}
    <div style={{ position:"absolute", top:"4%", left:"33%", width:"10%", height:"40%",
      background:"linear-gradient(180deg,#E83030,#C02020)",
      borderRadius:"6px 6px 0 40%" }} />
    {/* TV on right */}
    <div style={{ position:"absolute", top:"12%", right:"6%", width:"32%", height:"22%",
      background:"#1A1A2E", borderRadius:8, border:"8px solid #2A2A4E",
      boxShadow:"0 6px 20px rgba(0,0,0,0.4)" }}>
      <div style={{ position:"absolute", inset:8,
        background:"linear-gradient(135deg,#FF6B6B,#FFE66D,#4ECDC4,#45B7D1)",
        borderRadius:4, opacity:0.85 }} />
      <div style={{ position:"absolute", bottom:-20, left:"42%", width:"16%", height:14,
        background:"#2A2A4E" }} />
      <div style={{ position:"absolute", bottom:-28, left:"28%", right:"28%", height:8,
        background:"#2A2A4E", borderRadius:4 }} />
    </div>
    {/* colorful couch */}
    <div style={{ position:"absolute", top:"48%", left:"5%", width:"42%", height:"22%",
      background:"#E84444", borderRadius:"14px 14px 6px 6px",
      boxShadow:"0 8px 20px rgba(0,0,0,0.3)" }}>
      <div style={{ position:"absolute", top:"8%", left:"4%", width:"40%", height:"84%",
        background:"#CC2222", borderRadius:10 }} />
      <div style={{ position:"absolute", top:"8%", right:"4%", width:"40%", height:"84%",
        background:"#CC2222", borderRadius:10 }} />
      {/* cushions */}
      {[{c:"#FF8800",x:"14%"},{c:"#FFE030",x:"42%"},{c:"#44BB44",x:"70%"}].map((p,i)=>(
        <div key={i} style={{ position:"absolute", bottom:"12%", left:p.x,
          width:"18%", height:"40%", background:p.c, borderRadius:8 }} />
      ))}
    </div>
    {/* side table with lamp */}
    <div style={{ position:"absolute", top:"52%", right:"20%", width:"8%", height:"18%",
      background:"#8B5E3C", borderRadius:"4px 4px 2px 2px",
      boxShadow:"0 4px 8px rgba(0,0,0,0.25)" }}>
      <div style={{ position:"absolute", top:"-55%", left:"-100%", right:"-100%", height:"60%",
        background:"#FFE090", borderRadius:"50% 50% 0 0",
        boxShadow:"0 0 30px rgba(255,220,100,0.8)" }} />
      <div style={{ position:"absolute", top:"-10%", left:"30%", width:"40%", height:"15%",
        background:"#AA7840", borderRadius:2 }} />
    </div>
    {/* family photos on wall */}
    {[{x:"48%",y:"8%",c:"#4488FF"},{x:"58%",y:"5%",c:"#FF4488"},{x:"68%",y:"9%",c:"#44CC44"}].map((f,i)=>(
      <div key={i} style={{ position:"absolute", top:f.y, left:f.x, width:"7%", height:"12%",
        background:"#FFFAF0", border:"4px solid #CCA060",
        borderRadius:4, boxShadow:"2px 2px 8px rgba(0,0,0,0.2)" }}>
        <div style={{ position:"absolute", inset:6, background:f.c, borderRadius:2, opacity:0.7 }} />
      </div>
    ))}
  </AbsoluteFill>
);

// ─── Kitchen ────────────────────────────────────────────────────────────────
const Kitchen: React.FC = () => (
  <AbsoluteFill>
    {/* cream walls */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"65%",
      background:"linear-gradient(180deg,#FFF8E8 0%,#FFF0CC 100%)" }} />
    {/* colorful backsplash tiles */}
    {[0,1,2,3,4,5,6,7,8,9].map(col=>[0,1,2,3].map(row=>(
      <div key={`${col}-${row}`} style={{ position:"absolute",
        top:`${22 + row*7}%`, left:`${col*10}%`,
        width:"9.5%", height:"6.5%",
        background:`hsl(${(col*37+row*23)%360},70%,78%)`,
        border:"2px solid rgba(255,255,255,0.8)", boxSizing:"border-box" }} />
    )))}
    {/* kitchen counter */}
    <div style={{ position:"absolute", top:"52%", left:0, right:0, height:"16%",
      background:"linear-gradient(180deg,#F0E8D8,#D8C8A8)" }} />
    <div style={{ position:"absolute", top:"51%", left:0, right:0, height:"3%",
      background:"linear-gradient(180deg,#FFFFFF,#E8E0D0)", borderRadius:"4px 4px 0 0" }} />
    {/* cabinet below counter */}
    <div style={{ position:"absolute", top:"68%", left:0, right:0, bottom:0,
      background:"linear-gradient(180deg,#D4A060,#B07840)" }}>
      {[0,33,66].map(x=>(
        <React.Fragment key={x}>
          <div style={{ position:"absolute", top:"5%", left:`${x+1}%`, width:"30%", bottom:"5%",
            border:"4px solid #906030", borderRadius:6 }} />
          <div style={{ position:"absolute", top:"46%", left:`${x+14}%`,
            width:10, height:10, borderRadius:"50%", background:"#C08840" }} />
        </React.Fragment>
      ))}
    </div>
    {/* colorful fridge on left */}
    <div style={{ position:"absolute", top:"5%", left:"2%", width:"18%", height:"62%",
      background:"linear-gradient(135deg,#F0F8FF,#E0F0F8)", borderRadius:"8px 8px 4px 4px",
      border:"4px solid #C8D8E8", boxShadow:"4px 0 12px rgba(0,0,0,0.2)" }}>
      {/* fridge magnets / drawings */}
      {[{x:"15%",y:"8%",c:"#FF4444",t:"A+"},{x:"50%",y:"6%",c:"#FF8800",t:"★"},{x:"20%",y:"24%",c:"#4488FF",t:"❤"}].map((m,i)=>(
        <div key={i} style={{ position:"absolute", top:m.y, left:m.x,
          width:32, height:32, background:m.c, borderRadius:4,
          display:"flex", alignItems:"center", justifyContent:"center",
          color:"white", fontSize:13, fontWeight:900, fontFamily:"sans-serif" }}>{m.t}</div>
      ))}
      <div style={{ position:"absolute", top:"44%", left:0, right:0, height:"3px",
        background:"#C8D8E8" }} />
      <div style={{ position:"absolute", top:"46%", right:"12%",
        width:8, height:8, borderRadius:"50%", background:"#A0B8C8" }} />
      <div style={{ position:"absolute", top:"16%", right:"12%",
        width:8, height:8, borderRadius:"50%", background:"#A0B8C8" }} />
    </div>
    {/* window above sink — morning light */}
    <div style={{ position:"absolute", top:"4%", left:"30%", right:"25%", height:"20%",
      background:"linear-gradient(180deg,#87CEEB,#B0E8FF)", border:"8px solid #FFF8EC",
      borderRadius:4, boxShadow:"0 4px 12px rgba(0,0,0,0.15)" }}>
      <div style={{ position:"absolute", top:0, bottom:0, left:"50%", width:4, background:"rgba(255,248,236,0.8)" }} />
      <div style={{ position:"absolute", top:"8%", right:"12%", width:18, height:18,
        borderRadius:"50%", background:"#FFE040", boxShadow:"0 0 16px #FFE040" }} />
    </div>
    {/* sink */}
    <div style={{ position:"absolute", top:"52%", left:"30%", width:"20%", height:"5%",
      background:"linear-gradient(180deg,#D0E8F0,#B0C8D8)", borderRadius:"4px 4px 8px 8px",
      border:"3px solid #B0C0D0" }}>
      <div style={{ position:"absolute", top:"20%", left:"44%", width:8, height:8,
        borderRadius:"50%", background:"#8AAABB" }} />
    </div>
    {/* colorful cereal boxes on counter */}
    {[{c:"#FF4444",x:"55%",t:"O"},{c:"#FF8800",x:"62%",t:"★"},{c:"#4488FF",x:"69%",t:"K"}].map((b,i)=>(
      <div key={i} style={{ position:"absolute", top:"40%", left:b.x,
        width:"6%", height:"14%", background:b.c, borderRadius:"3px 3px 0 0",
        boxShadow:"2px 2px 4px rgba(0,0,0,0.2)",
        display:"flex", alignItems:"center", justifyContent:"center",
        color:"white", fontSize:16, fontWeight:900, fontFamily:"sans-serif" }}>{b.t}</div>
    ))}
    {/* fruit bowl */}
    <div style={{ position:"absolute", top:"50%", left:"78%", width:"14%", height:"6%",
      background:"#E8C870", borderRadius:"50%", border:"3px solid #C0A040" }}>
      {[{c:"#FF4444",l:"10%"},{c:"#FF8800",l:"35%"},{c:"#88CC44",l:"60%"}].map((f,i)=>(
        <div key={i} style={{ position:"absolute", top:"-40%", left:f.l,
          width:18, height:18, borderRadius:"50%", background:f.c }} />
      ))}
    </div>
    {/* steam from coffee */}
    <div style={{ position:"absolute", top:"44%", left:"84%", width:"5%", height:"10%",
      background:"#FF6633", borderRadius:"4px 4px 0 0",
      border:"3px solid #CC4400" }} />
  </AbsoluteFill>
);

// ─── Bedroom ────────────────────────────────────────────────────────────────
const Bedroom: React.FC = () => (
  <AbsoluteFill>
    {/* deep purple-blue wall — cozy night vibe */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"68%",
      background:"linear-gradient(180deg,#1A0A40 0%,#2E1060 40%,#3C1880 100%)" }} />
    {/* glow-in-dark stars */}
    {[{x:10,y:5},{x:25,y:12},{x:40,y:4},{x:55,y:9},{x:70,y:6},{x:82,y:15},{x:15,y:22},{x:60,y:20},{x:88,y:8}].map((s,i)=>(
      <div key={i} style={{ position:"absolute", top:`${s.y}%`, left:`${s.x}%`,
        width:6, height:6, borderRadius:"50%", background:"#FFFFAA",
        boxShadow:`0 0 ${6+i%3*4}px #FFFFAA`, opacity:0.8+i%3*0.1 }} />
    ))}
    {/* moon */}
    <div style={{ position:"absolute", top:"6%", right:"10%", width:"9%", height:"9%",
      borderRadius:"50%", background:"#FFF5CC",
      boxShadow:"0 0 30px #FFF5CC, 0 0 60px rgba(255,245,200,0.3)" }} />
    {/* light purple carpet */}
    <div style={{ position:"absolute", top:"68%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#AA80CC,#8860AA)" }} />
    {/* colorful rug */}
    <div style={{ position:"absolute", top:"72%", left:"15%", right:"15%", height:"14%",
      background:"radial-gradient(ellipse,#FF6699,#FF99CC 40%,#CC66AA 100%)",
      borderRadius:"50%", border:"8px solid #FF44AA" }} />
    {/* colorful bed */}
    <div style={{ position:"absolute", top:"44%", left:"4%", width:"45%", height:"28%",
      background:"#FF6699", borderRadius:"12px 12px 4px 4px",
      boxShadow:"0 8px 24px rgba(0,0,0,0.4)" }}>
      {/* pillow */}
      <div style={{ position:"absolute", top:"8%", left:"4%", width:"40%", height:"35%",
        background:"#FFFFFF", borderRadius:8, border:"3px solid #FFCCDD" }} />
      <div style={{ position:"absolute", top:"8%", right:"4%", width:"40%", height:"35%",
        background:"#FFFACC", borderRadius:8, border:"3px solid #FFEEBB" }} />
      {/* colorful blanket */}
      <div style={{ position:"absolute", top:"40%", left:0, right:0, bottom:0,
        background:"linear-gradient(90deg,#FF88AA,#FFAACC,#CC66AA,#FF88CC)",
        borderRadius:"0 0 4px 4px" }} />
      {/* stuffed animal on bed */}
      <div style={{ position:"absolute", top:"-18%", right:"8%",
        width:"16%", height:"30%", background:"#FF8800", borderRadius:"50% 50% 40% 40%" }}>
        <div style={{ position:"absolute", top:"-30%", left:"10%", width:"36%", height:"36%",
          borderRadius:"50%", background:"#FF8800" }} />
        <div style={{ position:"absolute", top:"-30%", right:"10%", width:"36%", height:"36%",
          borderRadius:"50%", background:"#FF8800" }} />
        <div style={{ position:"absolute", top:"30%", left:"25%", width:"10px", height:"10px",
          borderRadius:"50%", background:"#333" }} />
        <div style={{ position:"absolute", top:"30%", right:"25%", width:"10px", height:"10px",
          borderRadius:"50%", background:"#333" }} />
      </div>
    </div>
    {/* nightstand */}
    <div style={{ position:"absolute", top:"55%", left:"52%", width:"10%", height:"16%",
      background:"#604080", borderRadius:4, border:"2px solid #402060" }}>
      {/* lamp */}
      <div style={{ position:"absolute", top:"-55%", left:"-20%", right:"-20%", height:"55%",
        background:"linear-gradient(180deg,#FFFACC,#FFE890)", borderRadius:"50% 50% 0 0",
        boxShadow:"0 0 20px rgba(255,240,150,0.8)" }} />
      <div style={{ position:"absolute", top:"-12%", left:"35%", width:"30%", height:"15%",
        background:"#6050A0" }} />
    </div>
    {/* rainbow poster on wall */}
    <div style={{ position:"absolute", top:"8%", left:"6%", width:"20%", height:"24%",
      background:"white", borderRadius:4, border:"6px solid #DDD",
      boxShadow:"2px 2px 8px rgba(0,0,0,0.3)" }}>
      {["#FF4444","#FF8800","#FFE040","#44CC44","#4488FF","#AA44CC"].map((c,i)=>(
        <div key={i} style={{ position:"absolute", top:`${10+i*13}%`, left:"8%", right:"8%",
          height:"10%", background:c, borderRadius:4 }} />
      ))}
    </div>
    {/* toys on floor */}
    {[{c:"#FF4444",x:"68%",s:22},{c:"#4488FF",x:"75%",s:18},{c:"#FFE040",x:"82%",s:20}].map((t,i)=>(
      <div key={i} style={{ position:"absolute", bottom:"8%", left:t.x,
        width:t.s, height:t.s, borderRadius:"50%", background:t.c }} />
    ))}
  </AbsoluteFill>
);

// ─── Bathroom ───────────────────────────────────────────────────────────────
const Bathroom: React.FC = () => (
  <AbsoluteFill>
    {/* aqua tiles wall */}
    {[0,1,2,3,4,5,6,7,8,9].map(col=>[0,1,2,3,4,5,6].map(row=>(
      <div key={`${col}-${row}`} style={{ position:"absolute",
        top:`${row*9.5}%`, left:`${col*10}%`,
        width:"9.4%", height:"9%",
        background:`hsl(${180+col*5},${60+row*4}%,${70+col%2*8}%)`,
        border:"3px solid rgba(255,255,255,0.9)", boxSizing:"border-box" }} />
    )))}
    {/* floor */}
    <div style={{ position:"absolute", top:"68%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#E8F8FF,#C8E8F8)" }}>
      {/* water puddle effect (Sem chaos!) */}
      {[{x:"10%",w:"30%"},{x:"50%",w:"40%"},{x:"20%",w:"60%"}].map((p,i)=>(
        <div key={i} style={{ position:"absolute", top:`${20+i*25}%`, left:p.x,
          width:p.w, height:"18%",
          background:`rgba(150,220,255,${0.35+i*0.1})`,
          borderRadius:"50%", boxShadow:"0 0 8px rgba(100,200,255,0.4)" }} />
      ))}
    </div>
    {/* white bathtub */}
    <div style={{ position:"absolute", top:"42%", left:"4%", width:"52%", height:"28%",
      background:"linear-gradient(180deg,#FFFFFF,#F0F8FF)", borderRadius:"16px 16px 24px 24px",
      border:"6px solid #E0EEF8", boxShadow:"0 8px 20px rgba(0,0,0,0.2)" }}>
      {/* water in tub — overflow! */}
      <div style={{ position:"absolute", inset:"15%", background:"linear-gradient(180deg,#60CCFF,#40AADE)",
        borderRadius:12, overflow:"hidden" }}>
        {/* soap bubbles */}
        {[{x:10,y:10,r:14},{x:35,y:5,r:18},{x:60,y:8,r:12},{x:80,y:12,r:16},{x:50,y:20,r:10}].map((b,i)=>(
          <div key={i} style={{ position:"absolute", left:`${b.x}%`, top:`${b.y}%`,
            width:b.r, height:b.r, borderRadius:"50%",
            background:"rgba(255,255,255,0.8)",
            boxShadow:`0 0 ${b.r/2}px rgba(255,255,255,0.5)` }} />
        ))}
      </div>
      {/* water spilling over tub */}
      <div style={{ position:"absolute", top:"-8%", left:"60%", right:"-2%", height:"20%",
        background:"rgba(100,200,255,0.7)", borderRadius:"0 0 12px 12px" }} />
    </div>
    {/* rubber duck */}
    <div style={{ position:"absolute", top:"38%", left:"32%",
      width:"8%", height:"10%", background:"#FFE040",
      borderRadius:"50% 50% 40% 40%",
      boxShadow:"0 4px 8px rgba(0,0,0,0.2)" }}>
      <div style={{ position:"absolute", top:"-40%", left:"20%", width:"60%", height:"60%",
        borderRadius:"50%", background:"#FFE040" }}>
        <div style={{ position:"absolute", top:"20%", left:"20%",
          width:6, height:6, borderRadius:"50%", background:"#333" }} />
        <div style={{ position:"absolute", top:"55%", left:"10%", right:"10%", height:"25%",
          background:"#FF8800", borderRadius:"0 0 6px 6px" }} />
      </div>
    </div>
    {/* toilet */}
    <div style={{ position:"absolute", top:"30%", right:"6%", width:"18%", height:"38%",
      background:"#FFFFFF", borderRadius:"12px 12px 8px 8px",
      border:"3px solid #E0EEF8", boxShadow:"2px 4px 12px rgba(0,0,0,0.15)" }}>
      <div style={{ position:"absolute", top:"-18%", left:"-5%", right:"-5%", height:"22%",
        background:"linear-gradient(180deg,#F0F8FF,#E0EEF8)", borderRadius:8,
        border:"3px solid #D0E8F0" }} />
    </div>
    {/* mirror with rainbow toothbrushes */}
    <div style={{ position:"absolute", top:"3%", right:"28%", width:"22%", height:"28%",
      background:"linear-gradient(135deg,rgba(200,240,255,0.6),rgba(240,255,255,0.8))",
      border:"8px solid #E0EEF8", borderRadius:6,
      boxShadow:"0 4px 12px rgba(0,0,0,0.2)" }} />
    {/* toothbrushes in cup */}
    <div style={{ position:"absolute", top:"48%", right:"28%", width:"7%", height:"8%",
      background:"#FF8888", borderRadius:"4px 4px 6px 6px" }}>
      {[{c:"#4488FF",r:"-30deg"},{c:"#FF4488",r:"0deg"},{c:"#44CC44",r:"25deg"}].map((b,i)=>(
        <div key={i} style={{ position:"absolute", bottom:"70%", left:`${10+i*28}%`,
          width:8, height:30, background:b.c, borderRadius:3,
          transform:`rotate(${b.r})`, transformOrigin:"bottom center" }} />
      ))}
    </div>
    {/* unrolled toilet paper chaos */}
    <div style={{ position:"absolute", top:"66%", left:"58%", right:"10%", height:"6%",
      background:"white", borderRadius:20, border:"2px solid #DDD",
      transform:"rotate(-8deg)", opacity:0.9 }} />
    <div style={{ position:"absolute", top:"72%", left:"40%", right:"20%", height:"5%",
      background:"white", borderRadius:20, border:"2px solid #DDD",
      transform:"rotate(12deg)", opacity:0.85 }} />
  </AbsoluteFill>
);

// ─── School ──────────────────────────────────────────────────────────────────
const School: React.FC = () => (
  <AbsoluteFill>
    {/* bright pastel yellow wall */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"65%",
      background:"linear-gradient(180deg,#FFF8CC 0%,#FFE880 100%)" }} />
    {/* alphabet border strip */}
    <div style={{ position:"absolute", top:"48%", left:0, right:0, height:"5%",
      background:"#FF8800", display:"flex", alignItems:"center", overflow:"hidden" }}>
      {"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((l,i)=>(
        <div key={i} style={{ color:["#FF4444","#4488FF","#44CC44","#FFEE00"][i%4],
          fontFamily:"sans-serif", fontWeight:900, fontSize:16,
          padding:"0 6px", textShadow:"1px 1px 0 rgba(0,0,0,0.2)" }}>{l}</div>
      ))}
    </div>
    {/* big chalkboard */}
    <div style={{ position:"absolute", top:"4%", left:"5%", right:"5%", height:"42%",
      background:"#1A6B3A", borderRadius:6, border:"10px solid #8B5500",
      boxShadow:"0 6px 24px rgba(0,0,0,0.4)" }}>
      {/* chalk writing */}
      <div style={{ position:"absolute", top:"20%", left:"8%", width:"38%", height:5,
        background:"rgba(255,255,255,0.75)", borderRadius:3 }} />
      <div style={{ position:"absolute", top:"40%", left:"10%", width:"25%", height:4,
        background:"rgba(255,255,255,0.55)", borderRadius:3 }} />
      <div style={{ position:"absolute", top:"60%", left:"8%", width:"42%", height:4,
        background:"rgba(255,255,255,0.6)", borderRadius:3 }} />
      {/* colorful math: 2+2=4 */}
      <div style={{ position:"absolute", top:"15%", right:"8%",
        color:"rgba(255,255,255,0.9)", fontFamily:"sans-serif", fontWeight:900, fontSize:28 }}>2+2=4</div>
      {/* smiley on board */}
      <div style={{ position:"absolute", bottom:"10%", right:"12%", width:40, height:40,
        borderRadius:"50%", border:"3px solid rgba(255,255,100,0.8)" }}>
        <div style={{ position:"absolute", top:"22%", left:"22%", width:8, height:8,
          borderRadius:"50%", background:"rgba(255,255,100,0.8)" }} />
        <div style={{ position:"absolute", top:"22%", right:"22%", width:8, height:8,
          borderRadius:"50%", background:"rgba(255,255,100,0.8)" }} />
      </div>
    </div>
    {/* chalk tray */}
    <div style={{ position:"absolute", top:"45%", left:"5%", right:"5%", height:"3.5%",
      background:"#8B5500", borderRadius:"0 0 6px 6px" }}>
      {[{c:"#FFF",x:"8%"},{c:"#FFE060",x:"16%"},{c:"#FF8080",x:"24%"},{c:"#88DDFF",x:"32%"}].map((c,i)=>(
        <div key={i} style={{ position:"absolute", left:c.x, top:"10%",
          width:"5%", height:"80%", background:c.c, borderRadius:2 }} />
      ))}
    </div>
    {/* colorful cubbies */}
    {[{c:"#FF6B6B",x:"2%"},{c:"#4ECDC4",x:"16%"},{c:"#FFE66D",x:"30%"},{c:"#CC88FF",x:"44%"}].map((cb,i)=>(
      <div key={i} style={{ position:"absolute", top:"14%", left:cb.x,
        width:"12%", height:"18%", background:cb.c, borderRadius:4,
        border:"3px solid rgba(0,0,0,0.15)",
        boxShadow:"2px 2px 6px rgba(0,0,0,0.2)" }}>
        <div style={{ position:"absolute", bottom:"8%", left:"20%", right:"20%", height:"10%",
          background:"rgba(0,0,0,0.15)", borderRadius:2 }} />
      </div>
    ))}
    {/* student artwork on wall */}
    {[{x:"62%",bg:"#FFD0D0"},{x:"74%",bg:"#D0F0D0"},{x:"86%",bg:"#D0D0FF"}].map((a,i)=>(
      <div key={i} style={{ position:"absolute", top:"6%", left:a.x, width:"10%", height:"14%",
        background:a.bg, border:"3px solid #AAA", borderRadius:2,
        boxShadow:"2px 2px 6px rgba(0,0,0,0.15)" }}>
        <div style={{ position:"absolute", inset:6,
          background:`hsl(${i*80},60%,60%)`, borderRadius:2, opacity:0.6 }} />
      </div>
    ))}
    {/* light wood floor */}
    <div style={{ position:"absolute", top:"65%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#E8C880,#C8A050)" }} />
    {[20,40,60,80].map(x=>(
      <div key={x} style={{ position:"absolute", top:"65%", bottom:0, left:`${x}%`,
        width:3, background:"rgba(0,0,0,0.1)" }} />
    ))}
    {/* colorful desk */}
    <div style={{ position:"absolute", top:"56%", left:"55%", right:"4%", height:"10%",
      background:"#A0D060", borderRadius:"4px 4px 0 0",
      boxShadow:"0 -3px 8px rgba(0,0,0,0.1)" }}>
      <div style={{ position:"absolute", top:"20%", left:"8%", width:"15%", height:"50%",
        background:"#FFF5", borderRadius:2 }} />
    </div>
  </AbsoluteFill>
);

// ─── Park ────────────────────────────────────────────────────────────────────
const Park: React.FC = () => (
  <AbsoluteFill>
    {/* vivid sky gradient */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"54%",
      background:"linear-gradient(180deg,#1488CC 0%,#2BC0E4 60%,#74D7F0 100%)" }} />
    {/* big sun */}
    <div style={{ position:"absolute", top:"5%", right:"10%", width:"12%", height:"12%",
      borderRadius:"50%", background:"#FFE040",
      boxShadow:"0 0 40px #FFE040, 0 0 80px rgba(255,224,64,0.4)" }} />
    {/* sun rays */}
    {[0,45,90,135,180,225,270,315].map(a=>(
      <div key={a} style={{ position:"absolute", top:"11%", right:"16%",
        width:"7%", height:4, background:"rgba(255,224,64,0.5)",
        transformOrigin:"0% 50%", transform:`rotate(${a}deg) translateX(70%)` }} />
    ))}
    {/* fluffy clouds */}
    {[{x:5,y:8,w:26},{x:38,y:5,w:32},{x:74,y:10,w:22}].map((c,i)=>(
      <React.Fragment key={i}>
        <div style={{ position:"absolute", top:`${c.y}%`, left:`${c.x}%`,
          width:`${c.w}%`, height:"7%", background:"#FFFFFF",
          borderRadius:50, boxShadow:"0 4px 16px rgba(0,0,0,0.1)" }} />
        <div style={{ position:"absolute", top:`${c.y-2.5}%`, left:`${c.x+4}%`,
          width:`${c.w*0.6}%`, height:"7%", background:"#FFFFFF", borderRadius:50 }} />
        <div style={{ position:"absolute", top:`${c.y-1.5}%`, left:`${c.x+c.w*0.4}%`,
          width:`${c.w*0.4}%`, height:"5.5%", background:"#FFFFFF", borderRadius:50 }} />
      </React.Fragment>
    ))}
    {/* bright grass */}
    <div style={{ position:"absolute", top:"50%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#2ECC40 0%,#27AE36 60%,#1E8A2A 100%)" }} />
    <div style={{ position:"absolute", top:"48%", left:0, right:0, height:"7%",
      background:"#3DD648", borderRadius:"60% 60% 0 0 / 100% 100% 0 0" }} />
    {/* colorful flowers */}
    {[{x:4,c:"#FF3344"},{x:9,c:"#FF88CC"},{x:14,c:"#FFEE30"},{x:78,c:"#FF6600"},{x:84,c:"#FF3388"},{x:90,c:"#AA44FF"}].map((f,i)=>(
      <React.Fragment key={i}>
        <div style={{ position:"absolute", bottom:"32%", left:`${f.x}%`,
          width:6, height:"10%", background:"#2A9A1A", borderRadius:3 }} />
        <div style={{ position:"absolute", bottom:"39%", left:`${f.x-1}%`,
          width:24, height:24, borderRadius:"50%", background:f.c,
          boxShadow:`0 0 12px ${f.c}88` }} />
        <div style={{ position:"absolute", bottom:"41%", left:`${f.x+0.2}%`,
          width:10, height:10, borderRadius:"50%", background:"#FFE840" }} />
      </React.Fragment>
    ))}
    {/* playground slide */}
    <div style={{ position:"absolute", bottom:"26%", left:"15%", width:"2%", height:"22%",
      background:"#AA8040", borderRadius:3 }} />
    <div style={{ position:"absolute", bottom:"26%", left:"22%", width:"2%", height:"22%",
      background:"#AA8040", borderRadius:3 }} />
    <div style={{ position:"absolute", bottom:"46%", left:"15%", right:"65%", height:"3%",
      background:"#CC9940", borderRadius:4 }} />
    <div style={{ position:"absolute", bottom:"26%", left:"8%", right:"60%", height:"22%",
      background:"linear-gradient(135deg,#FF6644,#FF4422)",
      borderRadius:"4px 4px 0 0", transform:"skewY(-30deg)", transformOrigin:"bottom left" }} />
    {/* big tree */}
    <div style={{ position:"absolute", bottom:"28%", right:"8%", width:"6%", height:"28%",
      background:"#7A4A24", borderRadius:"4px 4px 8px 8px" }} />
    <div style={{ position:"absolute", bottom:"50%", right:"2%", width:"18%", height:"24%",
      background:"#22AA22", borderRadius:"60% 60% 50% 50%",
      boxShadow:"inset -6px -8px 16px rgba(0,0,0,0.3)" }} />
    <div style={{ position:"absolute", bottom:"60%", right:"4%", width:"12%", height:"18%",
      background:"#33CC33", borderRadius:"50% 50% 40% 40%" }} />
    {/* path */}
    <div style={{ position:"absolute", bottom:0, left:"30%", right:"30%", height:"30%",
      background:"linear-gradient(180deg,#E8D878,#C8B840)",
      borderRadius:"30% 30% 0 0 / 20% 20% 0 0" }} />
  </AbsoluteFill>
);

// ─── Shop ────────────────────────────────────────────────────────────────────
const Shop: React.FC = () => (
  <AbsoluteFill>
    {/* white ceiling */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"8%",
      background:"#F8F8F8" }} />
    {/* neon rainbow banner */}
    <div style={{ position:"absolute", top:"3%", left:"8%", right:"8%", height:"5%",
      background:"linear-gradient(90deg,#FF2244,#FF6622,#FFCC00,#44DD44,#2266FF,#AA44FF)",
      borderRadius:8, boxShadow:"0 0 20px rgba(255,100,0,0.45)" }}>
      <div style={{ position:"absolute", inset:0, display:"flex", alignItems:"center",
        justifyContent:"center", color:"white", fontFamily:"sans-serif",
        fontWeight:900, fontSize:18, textShadow:"0 1px 4px rgba(0,0,0,0.4)",
        letterSpacing:3 }}>SUPER STORE</div>
    </div>
    {/* back wall */}
    <div style={{ position:"absolute", top:"8%", left:0, right:0, height:"58%",
      background:"linear-gradient(180deg,#FFFAF2,#FFF5E0)" }} />
    {/* 3 shelf rows with colorful products */}
    {[{y:22,shade:"#F55"},{y:38,shade:"#55F"},{y:54,shade:"#5C5"}].map(({y,shade})=>(
      <React.Fragment key={y}>
        <div style={{ position:"absolute", top:`${y}%`, left:"2%", right:"2%",
          height:"3%", background:"#A07040", borderRadius:4,
          boxShadow:"0 4px 10px rgba(0,0,0,0.25)" }} />
        {[6,14,22,30,38,46,54,62,70,78,86].map((x,i)=>(
          <div key={x} style={{ position:"absolute", top:`${y-10}%`, left:`${x}%`,
            width:"7%", height:"11%",
            background:`hsl(${i*34+y*3},80%,60%)`,
            borderRadius:4, boxShadow:"1px 2px 4px rgba(0,0,0,0.2)" }}>
            <div style={{ position:"absolute", top:"10%", left:"10%", right:"10%", height:"20%",
              background:"rgba(255,255,255,0.5)", borderRadius:2 }} />
          </div>
        ))}
      </React.Fragment>
    ))}
    {/* floor — bright checkered */}
    <div style={{ position:"absolute", top:"66%", bottom:0, left:0, right:0,
      background:"#F5F5F5" }}>
      {[0,1,2,3,4].map(row=>[0,1,2,3,4,5,6,7,8,9].map(col=>(
        (row+col)%2===0 &&
        <div key={`${row}-${col}`} style={{ position:"absolute",
          top:`${row*20}%`, left:`${col*10}%`,
          width:"10%", height:"20%", background:"#E0E0E0" }} />
      )))}
    </div>
    {/* SALE sign */}
    <div style={{ position:"absolute", top:"14%", right:"4%", width:"12%", height:"8%",
      background:"#FF2244", borderRadius:8, display:"flex", alignItems:"center",
      justifyContent:"center", boxShadow:"0 4px 16px rgba(255,34,68,0.5)",
      transform:"rotate(-5deg)" }}>
      <div style={{ color:"#FFF", fontSize:22, fontWeight:900, fontFamily:"sans-serif",
        textShadow:"1px 1px 0 rgba(0,0,0,0.3)" }}>SALE!</div>
    </div>
    {/* shopping cart */}
    <div style={{ position:"absolute", bottom:"20%", left:"6%", width:"14%", height:"14%",
      border:"5px solid #888", borderRadius:4, borderTop:"none" }}>
      <div style={{ position:"absolute", top:"-40%", left:"-5%", right:"-5%", height:"40%",
        border:"5px solid #888", borderTop:"none", borderBottom:"none", borderRadius:4 }} />
      <div style={{ position:"absolute", bottom:"-30%", left:"15%",
        width:14, height:14, borderRadius:"50%", background:"#888" }} />
      <div style={{ position:"absolute", bottom:"-30%", right:"15%",
        width:14, height:14, borderRadius:"50%", background:"#888" }} />
    </div>
  </AbsoluteFill>
);

// ─── Street ──────────────────────────────────────────────────────────────────
const Street: React.FC = () => (
  <AbsoluteFill>
    {/* vivid sky */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"50%",
      background:"linear-gradient(180deg,#1A80E8 0%,#60BBFF 65%,#90D8FF 100%)" }} />
    {/* sun */}
    <div style={{ position:"absolute", top:"6%", left:"48%", width:"9%", height:"9%",
      transform:"translateX(-50%)", borderRadius:"50%", background:"#FFE530",
      boxShadow:"0 0 30px #FFE530, 0 0 60px rgba(255,229,48,0.4)" }} />
    {/* clouds */}
    {[{x:5,y:8,w:20},{x:55,y:5,w:28}].map((c,i)=>(
      <React.Fragment key={i}>
        <div style={{ position:"absolute", top:`${c.y}%`, left:`${c.x}%`,
          width:`${c.w}%`, height:"6%", background:"#FFF", borderRadius:50 }} />
        <div style={{ position:"absolute", top:`${c.y-2}%`, left:`${c.x+3}%`,
          width:`${c.w*0.55}%`, height:"6%", background:"#FFF", borderRadius:50 }} />
      </React.Fragment>
    ))}
    {/* colorful buildings */}
    {[
      {x:0,w:23,h:54,c:"#FF7055",wc:"#FFE8CC"},
      {x:21,w:18,h:42,c:"#5599FF",wc:"#CCE4FF"},
      {x:37,w:26,h:60,c:"#66DD66",wc:"#DDFFD0"},
      {x:61,w:20,h:46,c:"#FFCC44",wc:"#FFF5BB"},
      {x:79,w:21,h:50,c:"#FF66AA",wc:"#FFDDEE"},
    ].map((b,i)=>(
      <div key={i} style={{ position:"absolute", bottom:"32%", left:`${b.x}%`,
        width:`${b.w}%`, height:`${b.h}%`, background:b.c,
        borderRadius:"8px 8px 0 0",
        boxShadow:"inset -6px 0 16px rgba(0,0,0,0.15)" }}>
        {[18,34,52,70].map(wy=>[20,55].map(wx=>(
          <div key={`${wx}-${wy}`} style={{ position:"absolute", left:`${wx}%`, top:`${wy}%`,
            width:"20%", height:"8%", background:b.wc, borderRadius:2,
            border:"2px solid rgba(0,0,0,0.1)" }} />
        )))}
        {/* door */}
        <div style={{ position:"absolute", bottom:0, left:"30%", right:"30%", height:"16%",
          background:"rgba(0,0,0,0.2)", borderRadius:"6px 6px 0 0" }} />
      </div>
    ))}
    {/* sidewalk */}
    <div style={{ position:"absolute", bottom:"14%", left:0, right:0, height:"20%",
      background:"linear-gradient(180deg,#E0D0A0,#C8B880)" }}>
      {[12,24,36,48,60,72,84].map(x=>(
        <div key={x} style={{ position:"absolute", top:0, bottom:0, left:`${x}%`,
          width:3, background:"rgba(0,0,0,0.08)" }} />
      ))}
    </div>
    {/* road */}
    <div style={{ position:"absolute", bottom:0, left:0, right:0, height:"16%",
      background:"#3A3A4A" }}>
      {[10,25,40,55,70,85].map(x=>(
        <div key={x} style={{ position:"absolute", top:"38%", left:`${x}%`,
          width:"7%", height:5, background:"#FFEE40", borderRadius:3, opacity:0.8 }} />
      ))}
    </div>
    {/* street lamp */}
    <div style={{ position:"absolute", bottom:"14%", left:"18%", width:"2%", height:"32%",
      background:"#445566", borderRadius:3 }}>
      <div style={{ position:"absolute", top:"-10%", right:0, width:32, height:10,
        background:"#8899AA", borderRadius:"8px 8px 0 0" }}>
        <div style={{ position:"absolute", bottom:0, right:4, width:10, height:10,
          borderRadius:"50%", background:"#FFEE80",
          boxShadow:"0 0 14px #FFEE80, 0 0 28px rgba(255,238,128,0.6)" }} />
      </div>
    </div>
  </AbsoluteFill>
);

// ─── Scene map (CSS fallbacks for scenes without photos) ────────────────────
const CSS_SCENES: Record<string, React.FC> = {
  home:     Home,
  kitchen:  Kitchen,
  bedroom:  Bedroom,
  bathroom: Bathroom,
  school:   School,
  park:     Park,
  shop:     Shop,
  street:   Street,
  office:   Home,
  library:  School,
  notebook: Home,
  desk:     Kitchen,
  pencilcase: Shop,
};

// ─── Animated shimmer overlay for cartoon mode ──────────────────────────────
const CartoonShimmer: React.FC = () => {
  const frame = useCurrentFrame();
  const glints = [
    { x: 12, y: 18, period: 75, phase: 0  },
    { x: 80, y: 12, period: 90, phase: 20 },
    { x: 6,  y: 62, period: 85, phase: 40 },
    { x: 86, y: 70, period: 70, phase: 60 },
    { x: 45, y: 6,  period: 95, phase: 15 },
    { x: 25, y: 88, period: 80, phase: 35 },
    { x: 72, y: 88, period: 100,phase: 55 },
  ];
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {glints.map((g, i) => {
        const t = (frame + g.phase) / g.period;
        const opacity = Math.max(0, Math.sin(t * 2 * Math.PI) * 0.55);
        const scale = 0.7 + Math.abs(Math.sin(t * Math.PI)) * 0.6;
        const rotate = t * 360;
        return (
          <div key={i} style={{
            position: "absolute",
            left: `${g.x}%`,
            top: `${g.y}%`,
            fontSize: 14,
            transform: `rotate(${rotate}deg) scale(${scale})`,
            opacity,
            pointerEvents: "none",
            userSelect: "none",
          }}>✦</div>
        );
      })}
    </AbsoluteFill>
  );
};

export const SceneBg: React.FC<{ label: string; animated?: boolean }> = ({ label, animated }) => {
  // cartoon mode → always use CSS-drawn backgrounds (more vibrant than photos)
  const Cmp = CSS_SCENES[label] ?? Home;
  if (animated) {
    return (
      <>
        <Cmp />
        <CartoonShimmer />
      </>
    );
  }
  if (PHOTO_SCENES.has(label)) return <PhotoBg label={label} />;
  return <Cmp />;
};

// ── Per-beat background — smooth crossfade when conversation changes scene ───
// Prefers real photos (with Ken Burns) for realism; CSS scenes are the fallback.
// Photos are portrait (1080x1920), so landscape renders keep the CSS scenes.
const SceneLayer: React.FC<{ label: string }> = ({ label }) => {
  const { width, height } = useVideoConfig();
  const photo = height > width ? photoForScene(label) : null;
  if (photo) return <PhotoBg label={photo} />;
  const Cmp = CSS_SCENES[label] ?? Home;
  return <Cmp />;
};

export const SceneTransitionBg: React.FC<{
  currentScene: string;
  prevScene: string;
  beatStartFrame: number;
}> = ({ currentScene, prevScene, beatStartFrame }) => {
  const frame = useCurrentFrame();
  const TRANS = 18; // 0.6s transition
  const t = Math.min(1, Math.max(0, (frame - beatStartFrame) / TRANS));

  return (
    <>
      <AbsoluteFill>
        {currentScene === prevScene || t >= 1
          ? <SceneLayer label={currentScene} />
          : <>
              <AbsoluteFill><SceneLayer label={prevScene} /></AbsoluteFill>
              <AbsoluteFill style={{ opacity: t }}><SceneLayer label={currentScene} /></AbsoluteFill>
            </>
        }
      </AbsoluteFill>
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "linear-gradient(180deg, rgba(0,0,0,0.10) 0%, rgba(0,0,0,0.02) 50%, rgba(0,0,0,0.26) 100%)",
      }} />
    </>
  );
};

// ── Dynamic cycling background — switches scene every 5 seconds ─────────────
const ALL_SCENE_ORDER = ["home", "kitchen", "park", "bedroom", "school", "shop", "street", "bathroom"];

export const DynamicSceneBg: React.FC<{ labels: string[] }> = ({ labels }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Build a cycle list: use script scenes + fill up to 5 unique scenes for variety
  const seen = new Set<string>();
  const cycle: string[] = [];
  for (const l of labels) {
    if (!seen.has(l) && CSS_SCENES[l]) { seen.add(l); cycle.push(l); }
  }
  for (const l of ALL_SCENE_ORDER) {
    if (cycle.length >= 5) break;
    if (!seen.has(l)) { seen.add(l); cycle.push(l); }
  }
  if (cycle.length === 0) cycle.push("home");

  const CYCLE = Math.round(fps * 5); // 5 seconds per scene
  const FADE = 14; // frames of crossfade

  const cyclePos = frame % CYCLE;
  const cycleIdx = Math.floor(frame / CYCLE) % cycle.length;
  const nextIdx = (cycleIdx + 1) % cycle.length;

  const nextOpacity = cyclePos >= CYCLE - FADE ? (cyclePos - (CYCLE - FADE)) / FADE : 0;

  const CurrentCmp = CSS_SCENES[cycle[cycleIdx]] ?? Home;
  const NextCmp = CSS_SCENES[cycle[nextIdx]] ?? Home;

  return (
    <>
      <AbsoluteFill>
        <CurrentCmp />
      </AbsoluteFill>
      {nextOpacity > 0 && (
        <AbsoluteFill style={{ opacity: nextOpacity }}>
          <NextCmp />
        </AbsoluteFill>
      )}
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "linear-gradient(180deg, rgba(0,0,0,0.12) 0%, rgba(0,0,0,0.04) 50%, rgba(0,0,0,0.28) 100%)",
      }} />
    </>
  );
};
