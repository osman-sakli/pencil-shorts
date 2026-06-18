import React from "react";
import { AbsoluteFill } from "remotion";

// All backgrounds are code-drawn (no image assets).

const Home: React.FC = () => (
  <AbsoluteFill style={{ background: "linear-gradient(180deg,#fde8c8 0%,#f9d4a0 55%,#c9956b 100%)" }}>
    {/* wall */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"68%",
      background:"linear-gradient(180deg,#fde8c8,#f5d99a)" }} />
    {/* baseboard */}
    <div style={{ position:"absolute", top:"66%", left:0, right:0, height:"4%",
      background:"#d4b896", borderTop:"3px solid #b8956a" }} />
    {/* floor */}
    <div style={{ position:"absolute", top:"70%", left:0, right:0, bottom:0,
      background:"linear-gradient(180deg,#c9956b,#a87654)" }} />
    {/* floor planks */}
    {[20,40,60,80].map(x => (
      <div key={x} style={{ position:"absolute", top:"70%", bottom:0, left:`${x}%`,
        width:2, background:"rgba(0,0,0,0.08)" }} />
    ))}
    {/* picture frame */}
    <div style={{ position:"absolute", top:"10%", right:"12%", width:"18%", height:"22%",
      border:"6px solid #b8956a", background:"#ffe4c4", borderRadius:4 }}>
      <div style={{ position:"absolute", inset:8, background:"linear-gradient(135deg,#ffd79e,#f5c07a)", borderRadius:2 }} />
    </div>
    {/* window */}
    <div style={{ position:"absolute", top:"8%", left:"10%", width:"22%", height:"28%",
      border:"6px solid #b8956a", background:"linear-gradient(180deg,#d0eaff,#a8d4f5)", borderRadius:4 }}>
      <div style={{ position:"absolute", top:0, bottom:0, left:"50%", width:3, background:"#b8956a" }} />
      <div style={{ position:"absolute", left:0, right:0, top:"50%", height:3, background:"#b8956a" }} />
    </div>
  </AbsoluteFill>
);

const School: React.FC = () => (
  <AbsoluteFill style={{ background:"#e8f4e8" }}>
    {/* wall */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"65%",
      background:"linear-gradient(180deg,#d4ecd4,#c8e4c8)" }} />
    {/* chalkboard */}
    <div style={{ position:"absolute", top:"6%", left:"8%", right:"8%", height:"38%",
      background:"#2d5a3d", borderRadius:6, border:"10px solid #8b6914",
      boxShadow:"0 4px 16px rgba(0,0,0,0.2)" }}>
      <div style={{ position:"absolute", inset:12, background:"#336b47", borderRadius:3, opacity:0.4 }} />
      {/* chalk lines */}
      {[30,50,70].map(y => (
        <div key={y} style={{ position:"absolute", left:"5%", right:"5%", top:`${y}%`,
          height:2, background:"rgba(255,255,255,0.18)" }} />
      ))}
    </div>
    {/* chalk tray */}
    <div style={{ position:"absolute", top:"43%", left:"8%", right:"8%", height:"3%",
      background:"#8b6914", borderRadius:"0 0 4px 4px" }} />
    {/* floor */}
    <div style={{ position:"absolute", top:"65%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#d4b896,#b89468)" }} />
    {/* tiles */}
    {[20,40,60,80].map(x => (
      <div key={x} style={{ position:"absolute", top:"65%", bottom:0, left:`${x}%`,
        width:2, background:"rgba(0,0,0,0.07)" }} />
    ))}
  </AbsoluteFill>
);

const Park: React.FC = () => (
  <AbsoluteFill>
    {/* sky */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"55%",
      background:"linear-gradient(180deg,#87CEEB,#b8e4f7)" }} />
    {/* clouds */}
    {[{x:15,y:8,w:22},{x:55,y:5,w:28},{x:78,y:12,w:18}].map((c,i) => (
      <div key={i} style={{ position:"absolute", top:`${c.y}%`, left:`${c.x}%`,
        width:`${c.w}%`, height:"5%", background:"#fff", borderRadius:50, opacity:0.9 }} />
    ))}
    {/* grass */}
    <div style={{ position:"absolute", top:"52%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#4a9c4a,#3a7a3a)" }} />
    {/* grass edge */}
    <div style={{ position:"absolute", top:"50%", left:0, right:0, height:"5%",
      background:"linear-gradient(180deg,#6aba5a,#4a9c4a)", borderRadius:"50% 50% 0 0 / 8px" }} />
    {/* tree trunk */}
    <div style={{ position:"absolute", top:"28%", right:"12%", width:"5%", height:"30%",
      background:"#8b5e3c", borderRadius:4 }} />
    {/* tree canopy */}
    <div style={{ position:"absolute", top:"10%", right:"6%", width:"18%", height:"26%",
      background:"#3d8b3d", borderRadius:"60% 60% 50% 50%",
      boxShadow:"inset -4px -4px 8px rgba(0,0,0,0.2)" }} />
    {/* path */}
    <div style={{ position:"absolute", top:"62%", bottom:0, left:"30%", right:"30%",
      background:"linear-gradient(180deg,#d4c490,#c8b878)", borderRadius:"40% 40% 0 0" }} />
  </AbsoluteFill>
);

const Shop: React.FC = () => (
  <AbsoluteFill style={{ background:"#f5f0e8" }}>
    {/* ceiling */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"8%",
      background:"#e8e0d0" }} />
    {/* back wall */}
    <div style={{ position:"absolute", top:"8%", left:0, right:0, height:"60%",
      background:"linear-gradient(180deg,#faf6ee,#f0e8d8)" }} />
    {/* shelves */}
    {[22,38,54].map(y => (
      <React.Fragment key={y}>
        <div style={{ position:"absolute", top:`${y}%`, left:"5%", right:"5%",
          height:"3%", background:"#c8a870", borderRadius:3, boxShadow:"0 2px 4px rgba(0,0,0,0.15)" }} />
        {/* items on shelf */}
        {[15,28,42,58,72,85].map(x => (
          <div key={x} style={{ position:"absolute", top:`${y-8}%`, left:`${x}%`,
            width:"6%", height:"8%", background:`hsl(${x*4},60%,65%)`, borderRadius:3 }} />
        ))}
      </React.Fragment>
    ))}
    {/* floor */}
    <div style={{ position:"absolute", top:"68%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#e8e0d4,#d4c8b8)" }} />
    {/* floor tiles */}
    {[25,50,75].map(x => (
      <div key={x} style={{ position:"absolute", top:"68%", bottom:0, left:`${x}%`,
        width:2, background:"rgba(0,0,0,0.06)" }} />
    ))}
  </AbsoluteFill>
);

const Office: React.FC = () => (
  <AbsoluteFill style={{ background:"#e8eef5" }}>
    {/* back wall */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"68%",
      background:"linear-gradient(180deg,#d8e4f0,#c8d8e8)" }} />
    {/* window */}
    <div style={{ position:"absolute", top:"5%", right:"8%", width:"26%", height:"32%",
      border:"5px solid #a8b8c8", background:"linear-gradient(180deg,#d0eaff,#c0e0f8)", borderRadius:3 }}>
      <div style={{ position:"absolute", top:0, bottom:0, left:"50%", width:3, background:"#a8b8c8" }} />
      <div style={{ position:"absolute", left:0, right:0, top:"45%", height:3, background:"#a8b8c8" }} />
      {/* blinds */}
      {[15,30,45,60,75,90].map(y => (
        <div key={y} style={{ position:"absolute", left:0, right:0, top:`${y}%`,
          height:1, background:"rgba(180,200,220,0.6)" }} />
      ))}
    </div>
    {/* desk */}
    <div style={{ position:"absolute", top:"60%", left:0, right:0, height:"10%",
      background:"linear-gradient(180deg,#c8b090,#b89870)", borderRadius:"6px 6px 0 0",
      boxShadow:"0 -2px 8px rgba(0,0,0,0.15)" }} />
    {/* monitor */}
    <div style={{ position:"absolute", top:"36%", left:"10%", width:"28%", height:"26%",
      border:"5px solid #88909a", background:"#1a2030", borderRadius:6 }}>
      <div style={{ position:"absolute", inset:6, background:"linear-gradient(135deg,#1e3a5f,#0f2040)" }}>
        {[25,45,65].map(y => (
          <div key={y} style={{ position:"absolute", left:"8%", top:`${y}%`, width:"60%",
            height:3, background:"rgba(100,180,255,0.4)", borderRadius:2 }} />
        ))}
      </div>
    </div>
    {/* floor */}
    <div style={{ position:"absolute", top:"70%", bottom:0, left:0, right:0,
      background:"linear-gradient(180deg,#a8b8c8,#8898a8)" }} />
  </AbsoluteFill>
);

const Street: React.FC = () => (
  <AbsoluteFill>
    {/* sky */}
    <div style={{ position:"absolute", top:0, left:0, right:0, height:"50%",
      background:"linear-gradient(180deg,#6ab0d8,#a0cce8)" }} />
    {/* buildings */}
    {[
      {x:0,w:24,h:52,c:"#c8b8a0"},{x:22,w:18,h:42,c:"#b8a890"},
      {x:58,w:22,h:48,c:"#d0c0a8"},{x:78,w:22,h:38,c:"#c0b098"}
    ].map((b,i) => (
      <div key={i} style={{ position:"absolute", bottom:"36%", left:`${b.x}%`,
        width:`${b.w}%`, height:`${b.h}%`, background:b.c, borderRadius:"3px 3px 0 0" }}>
        {/* windows */}
        {[20,40,60,80].map(wy => [25,55,75].map(wx => (
          <div key={`${wx}-${wy}`} style={{ position:"absolute", left:`${wx}%`, top:`${wy}%`,
            width:"14%", height:"10%", background:"#d4e8f4", border:"1px solid #a0b0c0" }} />
        )))}
      </div>
    ))}
    {/* sidewalk */}
    <div style={{ position:"absolute", bottom:"18%", left:0, right:0, height:"20%",
      background:"linear-gradient(180deg,#d0c8b8,#c0b8a8)" }}>
      {[20,40,60,80].map(x => (
        <div key={x} style={{ position:"absolute", top:0, bottom:0, left:`${x}%`,
          width:2, background:"rgba(0,0,0,0.06)" }} />
      ))}
    </div>
    {/* road */}
    <div style={{ position:"absolute", bottom:0, left:0, right:0, height:"20%",
      background:"#444" }}>
      <div style={{ position:"absolute", top:"45%", left:0, right:0, height:6,
        background:"#f5f0c0", opacity:0.6 }} />
    </div>
    {/* lamp post */}
    <div style={{ position:"absolute", bottom:"18%", right:"20%", width:"2%", height:"32%",
      background:"#888", borderRadius:2 }}>
      <div style={{ position:"absolute", top:0, right:0, width:32, height:8,
        background:"#aaa", borderRadius:"8px 8px 0 0" }}>
        <div style={{ position:"absolute", bottom:0, right:4, width:6, height:6,
          background:"#ffe87a", borderRadius:"50%", boxShadow:"0 0 8px #ffe87a" }} />
      </div>
    </div>
  </AbsoluteFill>
);

const SCENES: Record<string, React.FC> = {
  home: Home, school: School, park: Park,
  shop: Shop, office: Office, street: Street,
  // legacy fallbacks
  notebook: Home, desk: Office, pencilcase: Shop,
};

export const SceneBg: React.FC<{ label: string }> = ({ label }) => {
  const Cmp = SCENES[label] ?? Home;
  return <Cmp />;
};
