(function(){
'use strict';
let RM=false;try{RM=matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}
const $=(s,r)=>(r||document).querySelector(s);
const $$=(s,r)=>Array.from((r||document).querySelectorAll(s));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pad2=n=>String(n).padStart(2,'0');
const WHO={'@ops':'Ops','@agents':'Agents','@leads':'Leads','@marketing':'Marketing','you':'You'};

/* ---------- the characters: one tile bot per engine ---------- */
// '#' body in the engine color, 'k' ink, 'w' paper. blink and act are rows swapped in for a frame.
const BOTS={
  // Ops is water: a droplet that sways and catches the light
  ops:{base:["......##......",".....####.....",".....####.....","....######....","...########...","..##########..","..#w########..",".#ww#########.",".#w##########.",".###kk###kk##.",".###kw###kw#d.",".###########d.",".####k###k##d.","..####kkk##d..","...#######d...",".....dddd....."],
    blink:{9:".############.",10:".###kk###kk#d."},
    idle:[{0:".......##.....",1:"......####...."},{0:".....##.......",1:"....####......"}],
    act:[{0:".......##.....",1:"......####....",6:"..##w#######..",7:".#w#w########.",8:".##w#########."},{0:".....##.......",1:"....####......"}],actN:4,actMs:190,hop:1},
  // Agents are earth: a little range of mountains with snow on top
  agents:{base:["......##......",".....#ww#.....","....#wwww#....","....#w##w#....","...#######d...","...########d..","..##########d.","..#kk####kk#d.",".##kw####kw##d",".############d","##k########k#d","###kkkkkkkk##d","#############d",".dddddddddddd."],
    blink:{7:"..##########d.",8:".##kk####kk##d"},
    act:[{10:"##k########k#d",11:"###kwwwwwwk##d"},{}]},
  // Leads is fire: a flame that never stops flickering
  leads:{base:[".....#........",".....##.....#.","..#..###...##.","..##.####.###.",".###.########.",".############.","##############","##############","##kk######kk##","##kw######kw##","##############","##k########k##","###kkkkkkkk###",".############.","..##########..","....dddddd...."],
    blink:{8:"##############",9:"##kk######kk##"},
    idle:[{0:"......#.......",1:"......##....#.",2:"..#..###...##.",3:".##..####.###."},{0:"....#.........",1:"....##......#.",2:".#..###....##.",3:".##.####..###."}],
    act:[{0:".....#.....#..",1:".#...##....##.",2:".##..###..###.",3:".###.####.####",12:"###kwwwwwwk###"},{0:"....#.........",1:"....##......#.",2:".#..###....##.",3:".##.####..###.",12:"###kwwwwwwk###"}],actN:6,actMs:140},
  // Marketing is wind: a cloud blowing your name somewhere new
  marketing:{base:[".....###...###.......","...#######.#####.....","..###############....",".#################...","##kk#####kk#######...","##kw#####kw######..##","#################.###","##########kkk####....","#########k...k##.####","##########kkk####....",".################.###","..##.#######.###...##"],
    blink:{4:"##################...",5:"##kk#####kk######..##"},
    idle:[{5:"##kw#####kw######...#",6:"#################..##",8:"#########k...k##..###",10:".################..##",11:"..##.#######.###....#"},{}],
    act:[{5:"##kw#####kw######...#",6:"#################..##",8:"#########k...k##..###",10:".################..##",11:"..##.#######.###....#"},{}],actN:6,actMs:140}
};
const BOT_LINES={
  ops:["Everything's where it should be.","Your morning summary is ready.","Nothing's late. I checked twice.","Sorted your clients A to Z. You're welcome.","Three things need you today. Just three."],
  agents:["Drafted it. Want a look?","Sorted 140 emails while you slept.","I'll ask before I send anything new.","Following up. Politely.","Reminders are out. Everyone confirmed."],
  leads:["Someone's interested!","Replied in 2 minutes. New record.","It's 10pm. I'm still here.","Quote sent. They're reading it now.","Hi! Want a price? Takes a minute."],
  marketing:["Your newsletter is ready for a look.","Welcome email 2 just went out.","Two blanks left on your page. Only you know those.","Version B is ahead. Two more days to be sure.","Sent from your own domain. Looks like you."]
};
function botSVG(name,over,crisp){
  const b=BOTS[name];if(!b)return '';
  const g=b.base.map((r,i)=>over&&over[i]!=null?over[i]:r),h=g.length,w=Math.max.apply(null,g.map(r=>r.length));
  const u=crisp?1:10,sz=crisp?1:9,o=crisp?0:.5;let s='';
  g.forEach((row,y)=>{for(let x=0;x<row.length;x++){const c=row[x];if(c==='.')continue;s+='<rect x="'+(x*u+o)+'" y="'+(y*u+o)+'" width="'+sz+'" height="'+sz+'" class="bt-'+(c==='#'?'b':c)+'"/>';}});
  return '<svg viewBox="0 0 '+(w*u)+' '+(h*u)+'"'+(crisp?' width="'+w+'" height="'+h+'" shape-rendering="crispEdges"':'')+' aria-hidden="true">'+s+'</svg>';
}
const BOT_MINI={};
function botTag(name){return '<span class="bot bot-mini" data-bot="'+name+'">'+(BOT_MINI[name]||(BOT_MINI[name]=botSVG(name,null,true)))+'</span>';}
const hasIO='IntersectionObserver' in window;
function once(els,fn,threshold){
  els=els.filter(Boolean);if(!els.length)return;
  if(!hasIO){els.forEach(fn);return;}
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){io.unobserve(e.target);fn(e.target);}}),{threshold:threshold||.35});
  els.forEach(el=>io.observe(el));
}

/* ---------- transitions (transitions.dev, adapted): timing comes from the CSS tokens ---------- */
const MS=(n,fb)=>{const v=parseFloat(getComputedStyle(document.documentElement).getPropertyValue(n));return Number.isFinite(v)?v:fb;};
// number pop-in: only the characters that changed pop, the shared start stays still
function setDigits(g,str,quiet){
  str=String(str);const prev=(g.dataset.v!=null?g.dataset.v:g.textContent).replace(/\s+/g,'');
  if(prev===str&&g.dataset.v!=null)return;g.dataset.v=str;g.setAttribute('aria-label',str);
  if(quiet||RM){g.textContent=str;return;}
  let same=0;while(same<prev.length&&same<str.length&&prev[same]===str[same])same++;
  g.classList.remove('is-animating');g.replaceChildren();
  str.split('').forEach((ch,i,all)=>{const s=document.createElement('span');s.className='t-digit';s.setAttribute('aria-hidden','true');s.textContent=ch;
    if(i<same)s.dataset.same='';if(i===all.length-2)s.dataset.stagger='1';else if(i===all.length-1)s.dataset.stagger='2';g.appendChild(s);});
  void g.offsetHeight;g.classList.add('is-animating');
}
// soft swap: old text blurs out while the new one blurs in, the width eases
function softSwap(el,next,quiet){
  const prev=el.dataset.text!=null?el.dataset.text:el.textContent;if(prev===next)return;el.dataset.text=next;clearTimeout(el._soft);
  if(quiet||RM){el.textContent=next;return;}
  const out=document.createElement('span');out.className='t-text-soft-old';out.setAttribute('aria-hidden','true');out.textContent=prev;
  const inn=document.createElement('span');inn.className='t-text-soft-new';inn.textContent=next;
  const w0=el.getBoundingClientRect().width;el.classList.remove('is-swapping');el.replaceChildren(out,inn);
  const w1=inn.getBoundingClientRect().width;el.style.width=w0+'px';void el.offsetWidth;el.classList.add('is-swapping');el.style.width=w1+'px';
  el._soft=setTimeout(()=>{el.classList.remove('is-swapping');el.style.removeProperty('width');el.textContent=next;},Math.max(MS('--text-soft-dur',200),MS('--text-soft-resize-dur',240))+40);
}
// text morph: shared letters stay put, only the part that differs cross-blurs
function morphText(el,next){
  const prev=el.dataset.text!=null?el.dataset.text:el.textContent;if(prev===next)return;el.dataset.text=next;clearTimeout(el._morph);
  if(RM){el.textContent=next;return;}
  let a=0;while(a<prev.length&&a<next.length&&prev[a]===next[a])a++;
  let b=0;while(b<prev.length-a&&b<next.length-a&&prev[prev.length-1-b]===next[next.length-1-b])b++;
  const sw=document.createElement('span');sw.className='t-morph-swap';
  const out=document.createElement('span');out.className='t-morph-old';out.setAttribute('aria-hidden','true');out.textContent=prev.slice(a,prev.length-b);
  const inn=document.createElement('span');inn.className='t-morph-new';inn.textContent=next.slice(a,next.length-b);sw.append(out,inn);
  el.textContent='';el.append(next.slice(0,a),sw,next.slice(next.length-b));
  sw.style.width=out.getBoundingClientRect().width+'px';void sw.offsetWidth;sw.classList.add('is-morphing');sw.style.width=inn.getBoundingClientRect().width+'px';
  el._morph=setTimeout(()=>{el.textContent=next;},Math.max(MS('--text-morph-dur',180),MS('--text-morph-resize-dur',240))+40);
}
// thinking line: the old state exits up, the new one rises in, both at once
function thinkSwap(box,next){
  const live=box.querySelector('.t-think-text:not(.is-exit)');if(!live)return;
  if(live.textContent===next)return;
  if(RM){live.textContent=next;live.setAttribute('data-text',next);return;}
  live.classList.add('is-exit');
  const n=live.cloneNode(false);n.className='t-think-text is-enter-start';n.textContent=next;n.setAttribute('data-text',next);box.appendChild(n);
  setTimeout(()=>{void n.offsetWidth;n.classList.remove('is-enter-start');},MS('--think-gap',50));
  setTimeout(()=>live.remove(),MS('--think-swap',150)+MS('--think-gap',50));
}
// matrix dot loader: sixteen dots, the variant is just a delay table
function matrix(el){
  if(el.childElementCount)return;const cyc=MS('--matrix-cycle',1200);
  for(let i=0;i<16;i++){const d=document.createElement('i');d.style.setProperty('--d',String(Math.round((i%4)*(cyc/10))));el.appendChild(d);}
}
// error shake: replay from a clean baseline
function shake(el){
  if(RM||!el)return;el.classList.add('t-input');el.classList.remove('is-shaking');void el.offsetWidth;el.classList.add('is-shaking');
  setTimeout(()=>el.classList.remove('is-shaking'),MS('--shake-dur-a',80)*2+MS('--shake-dur-b',60)*2+20);
}

/* ---------- decode ---------- */
const UP='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+=/<>[]{}_';
const LO='abcdefghijklmnopqrstuvwxyz0123456789#%&*+=/<>_';
const CAPS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
const recs=new WeakMap();
const pick=s=>s[Math.random()*s.length|0];
function decode(el,dur,glyphs){
  if(RM||!el) return;
  let r=recs.get(el);
  if(!r){
    const nodes=[],w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
    while(w.nextNode()) if(w.currentNode.nodeValue.trim()) nodes.push(w.currentNode);
    r={nodes,finals:nodes.map(n=>n.nodeValue),id:0};
    recs.set(el,r);
    if(!el.hasAttribute('aria-label'))el.setAttribute('aria-label',r.finals.join('').replace(/\s+/g,' ').trim());
  }
  const id=++r.id,total=r.finals.join('').length;
  if(!total) return;
  dur=dur||Math.min(1500,380+total*20);
  let off=0;
  const at=r.finals.map(s=>{const a=[];for(let i=0;i<s.length;i++)a.push(((off+i)/total)*dur*.62+Math.random()*dur*.38);off+=s.length;return a;});
  const cur=r.finals.map(s=>s.split(''));
  const t0=performance.now();let last=0;
  function frame(now){
    if(r.id!==id) return;
    const e=now-t0,swap=now-last>50;if(swap) last=now;
    let done=true;
    r.finals.forEach((f,k)=>{
      for(let i=0;i<f.length;i++){
        const c=f[i];
        if(/\s/.test(c)||e>=at[k][i]) cur[k][i]=c;
        else{done=false;if(swap||cur[k][i]===c) cur[k][i]=glyphs?pick(glyphs):(c>='a'&&c<='z'?pick(LO):pick(UP));}
      }
      r.nodes[k].nodeValue=cur[k].join('');
    });
    if(!done) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
function redecode(el,text,dur){
  if(!el)return;
  const r=recs.get(el);if(r)r.id++;
  recs.delete(el);el.removeAttribute('aria-label');el.textContent=text;decode(el,dur);
}
function onHover(el,fn){if(!el)return;el.addEventListener('mouseenter',fn);el.addEventListener('focus',fn);}

/* ---------- clock ---------- */
(function(){
  const els=$$('[data-clock]');let tz='';
  try{const p=new Intl.DateTimeFormat('en-US',{timeZoneName:'short'}).formatToParts(new Date()).find(x=>x.type==='timeZoneName');tz=p?p.value:''}catch(e){}
  let prev='';
  const tick=()=>{const d=new Date(),s=pad2(d.getHours())+pad2(d.getMinutes());if(s===prev)return;prev=s;
    els.forEach(el=>{el.innerHTML=pad2(d.getHours())+'<span class="c">:</span>'+pad2(d.getMinutes())+(tz?' '+esc(tz):'')});};
  tick();setInterval(tick,1000);
  $$('[data-year]').forEach(y=>y.textContent=String(new Date().getFullYear()));
})();

/* ---------- thumbnail placeholders ---------- */
const RAMP=' .:-=+*#%@',PAPER='242,242,239';
const TA=[0,.07,.13,.2,.28,.36,.45,.55,.66,.78];
function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function fieldFor(seed){
  const r=rng(seed*9973+17);
  const f1=3+r()*7,f2=3+r()*7,f3=2+r()*6,p1=r()*6.28,p2=r()*6.28,p3=r()*6.28,cx=.2+r()*.6,cy=.2+r()*.6,k=14+r()*22,tilt=r()<.5?1:-1;
  return (u,v)=>{
    let s=Math.sin(u*f1+p1)+Math.sin(v*f2+p2)+Math.sin((u+tilt*v)*f3+p3);
    const dx=(u-cx)*1.78,dy=v-cy;s+=Math.sin(Math.sqrt(dx*dx+dy*dy)*k)*1.2;
    let n=(s+4.2)/8.4;n=n<0?0:n>1?1:n;return n*n;
  };
}
function sizeCanvas(cv){
  const dpr=Math.min(2,window.devicePixelRatio||1),r=cv.getBoundingClientRect();
  const w=Math.max(1,r.width),h=Math.max(1,r.height);
  cv.width=Math.round(w*dpr);cv.height=Math.round(h*dpr);
  const ctx=cv.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);
  return {ctx,w,h};
}
function drawMini(cv,seed){
  if(!cv||!cv.getContext)return;
  const {ctx,w,h}=sizeCanvas(cv),F=fieldFor(seed),c=3;
  ctx.clearRect(0,0,w,h);
  for(let y=0;y<h;y+=c)for(let x=0;x<w;x+=c){
    const l=Math.min(9,F((x+1)/w,(y+1)/h)*10|0);if(!l)continue;
    ctx.fillStyle='rgba('+PAPER+','+TA[l]+')';ctx.fillRect(x,y,c-1,c-1);
  }
}
function drawThumb(cv,seed,anim){
  if(!cv||!cv.getContext)return;
  const {ctx,w,h}=sizeCanvas(cv);cv._w=w;
  ctx.font='400 11px "Martian Mono", ui-monospace, Menlo, monospace';ctx.textBaseline='top';
  const cw=ctx.measureText('M').width+3,ch=15,cols=Math.ceil(w/cw),rows=Math.ceil(h/ch),F=fieldFor(seed);
  const lv=new Uint8Array(cols*rows);
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)lv[y*cols+x]=Math.min(9,F((x+.5)*cw/w,(y+.5)*ch/h)*10|0);
  const paint=src=>{
    ctx.clearRect(0,0,w,h);
    for(let l=1;l<10;l++){
      ctx.fillStyle='rgba('+PAPER+','+TA[l]+')';const g=RAMP[l];
      for(let i=0;i<src.length;i++)if(src[i]===l)ctx.fillText(g,(i%cols)*cw,(i/cols|0)*ch);
    }
  };
  const id={};cv._id=id;cv._busy=false;
  if(!anim||RM){paint(lv);return;}
  cv._busy=true;
  const dur=900,at=new Float32Array(lv.length),cur=new Uint8Array(lv.length);
  for(let i=0;i<lv.length;i++){at[i]=((i%cols)/cols)*dur*.62+Math.random()*dur*.38;cur[i]=Math.random()*10|0;}
  const t0=performance.now();let last=0;
  function f(now){
    if(cv._id!==id||!cv.isConnected)return;
    const e=now-t0,swap=now-last>50;if(swap)last=now;let done=true;
    for(let i=0;i<lv.length;i++){
      if(e>=at[i])cur[i]=lv[i];
      else{done=false;if(swap)cur[i]=Math.random()<.45?0:Math.random()*10|0;}
    }
    if(swap||done)paint(cur);
    if(done)cv._busy=false;else requestAnimationFrame(f);
  }
  requestAnimationFrame(f);
}
const seedOf=cv=>+cv.dataset.seed||1;
function drawAllMinis(){$$('.mini canvas[data-seed]').forEach(cv=>drawMini(cv,seedOf(cv)));}
function refreshThumbs(force){
  $$('.thumb canvas[data-seed]').forEach(cv=>{
    if(cv._busy)return;
    const w=cv.getBoundingClientRect().width;
    if(force||Math.abs(w-(cv._w||0))>1)drawThumb(cv,seedOf(cv),false);
  });
}
drawAllMinis();refreshThumbs(true);
if(!RM)once($$('.thumb canvas[data-seed]'),cv=>drawThumb(cv,seedOf(cv),true),.3);

/* ---------- pixel icons ---------- */
const ICONS={
  discuss:['.########.','#........#','#.######.#','#........#','#.####...#','#........#','.########.','.##.......','.#........','..........'],
  build:['..........','..........','...####...','...#..#...','...####...','..........','####..####','#..#..#..#','####..####','..........'],
  implement:['....##....','....##....','....##....','..######..','...####...','....##....','..........','#........#','#........#','##########'],
  measure:['..........','#.......##','#.......##','#....##.##','#....##.##','#.##.##.##','#.##.##.##','#.##.##.##','##########','..........'],
  system:['..........','.###..###.','.###..###.','.###..###.','..........','..........','.###..###.','.###..###.','.###..###.','..........'],
  agent:['##########','#........#','#.#......#','#..#.....#','#...#....#','#..#.....#','#.#..###.#','#........#','##########','..........'],
  lead:['..........','##########','.########.','..######..','...####...','....##....','....##....','....##....','....##....','..........']
};
function buildIcon(svg){
  const bm=ICONS[svg.dataset.icon];if(!bm)return;
  let h='';
  for(let y=0;y<10;y++)for(let x=0;x<10;x++)h+='<rect x="'+x*5+'" y="'+y*5+'" width="4" height="4"'+(bm[y][x]==='#'?' class="on"':'')+'/>';
  svg.innerHTML=h;svg._r=Array.from(svg.children);svg._fin=svg._r.map((r,i)=>bm[i/10|0][i%10]==='#');
}
function pixDecode(svg,dur){
  if(RM||!svg||!svg._r)return;
  const rects=svg._r,fin=svg._fin,id={};svg._id=id;
  const at=rects.map((r,i)=>((i%10)/10)*dur*.62+Math.random()*dur*.38);
  const t0=performance.now();let last=0;
  function f(now){
    if(svg._id!==id)return;
    const e=now-t0,swap=now-last>50;if(swap)last=now;let done=true;
    rects.forEach((r,i)=>{
      if(e>=at[i])r.classList.toggle('on',fin[i]);
      else{done=false;if(swap)r.classList.toggle('on',Math.random()<.42);}
    });
    if(!done)requestAnimationFrame(f);
  }
  requestAnimationFrame(f);
}
$$('.px').forEach(buildIcon);
$$('.step,.svc,.tk-step').forEach(s=>s.addEventListener('mouseenter',()=>{decode($('.h3',s),360);pixDecode($('.px',s),420);}));
if(!RM)once([$('.steps'),$('.offer'),$('.track')],el=>$$('.px',el).forEach((svg,i)=>setTimeout(()=>pixDecode(svg,900),i*140)));

/* ---------- hero ASCII field ---------- */
(function(){
  const cv=$('#field'),hero=$('#hero'),ro=$('#readout');if(!cv||!hero||!cv.getContext)return;
  const ctx=cv.getContext('2d'),CH=15;
  const A=[0,.055,.11,.165,.225,.29,.355,.42,.49,.56];
  let W=0,H=0,cw=9,cols=0,rows=0,mx=-999,my=-999,on=false,raf=0,last=0;const t0=performance.now();
  function size(){
    const dpr=Math.min(2,window.devicePixelRatio||1),r=hero.getBoundingClientRect();
    W=r.width;H=r.height;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.font='400 11px "Martian Mono", ui-monospace, Menlo, monospace';ctx.textBaseline='top';
    cw=ctx.measureText('M').width+3;cols=Math.ceil(W/cw)+1;rows=Math.ceil(H/CH)+1;
  }
  function draw(now){
    const t=(now-t0)/1000,cx=cols*.74,cy=rows*.40,k=CH/cw,B=[[],[],[],[],[],[],[],[],[],[]];
    for(let y=0;y<rows;y++){
      const dy=(y-cy)*k,my2=(y-my)*k;
      for(let x=0;x<cols;x++){
        let v=Math.sin(x*.11+t*.45)+Math.sin(y*.21-t*.38)+Math.sin((x+y)*.07+t*.27);
        const dx=x-cx,d=Math.sqrt(dx*dx+dy*dy);v+=Math.sin(d*.32-t*1.4)*1.2;
        if(mx>-900){const ex=x-mx,dm=Math.sqrt(ex*ex+my2*my2);if(dm<14)v+=Math.sin(dm*.9-t*5)*(1-dm/14)*1.6;}
        let n=(v+4.2)/8.4;n=n<0?0:n>1?1:n;n*=n;
        const li=Math.min(9,n*10|0);if(li)B[li].push(x,y);
      }
    }
    ctx.clearRect(0,0,W,H);
    for(let l=1;l<10;l++){const b=B[l];if(!b.length)continue;ctx.fillStyle='rgba('+PAPER+','+A[l]+')';const g=RAMP[l];
      for(let i=0;i<b.length;i+=2)ctx.fillText(g,b[i]*cw,b[i+1]*CH);}
  }
  function loop(now){raf=requestAnimationFrame(loop);if(now-last<40)return;last=now;draw(now);}
  function start(){if(on||RM)return;on=true;raf=requestAnimationFrame(loop);}
  function stop(){on=false;cancelAnimationFrame(raf);}
  size();draw(t0);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{size();draw(performance.now());});
  if('ResizeObserver' in window)new ResizeObserver(()=>{size();draw(performance.now());}).observe(hero);
  if(!RM){
    if(hasIO)new IntersectionObserver(es=>{es[0].isIntersecting?start():stop();}).observe(hero);else start();
    document.addEventListener('visibilitychange',()=>{document.hidden?stop():start();});
    hero.addEventListener('pointermove',e=>{const r=hero.getBoundingClientRect(),px=e.clientX-r.left,py=e.clientY-r.top;mx=px/cw;my=py/CH;
      if(ro)ro.textContent='x '+String(Math.max(0,Math.round(px))).padStart(4,'0')+' · y '+String(Math.max(0,Math.round(py))).padStart(4,'0');});
    hero.addEventListener('pointerleave',()=>{mx=-999;my=-999;});
  }
})();

/* ---------- home work preview ---------- */
(function(){
  const pv=$('#preview');if(!pv)return;
  const rows=$$('.case-row[data-seed]');if(!rows.length)return;
  const fig=$('.thumb',pv),cv=$('canvas',fig),img=$('img',fig),tags=$$('.tag',fig);
  const name=$('.pv-name',pv),path=$('.pv-path',pv),num=$('.pv-num',pv),sum=$('.pv-sum',pv),go=$('.pv-go',pv);
  let cur=0;
  function show(i){
    if(i===cur)return;cur=i;const r=rows[i];
    rows.forEach((x,k)=>x.classList.toggle('on',k===i));
    path.textContent='Case study';
    num.textContent='case '+r.dataset.n+' / '+pad2(rows.length);
    redecode(name,r.dataset.name);
    sum.textContent=r.dataset.sum;
    go.href=r.getAttribute('href');
    if(r.dataset.img&&img){img.src=r.dataset.img;img.alt=r.dataset.name+' case image';img.hidden=false;cv.hidden=true;tags.forEach(t=>t.hidden=true);}
    else{if(img)img.hidden=true;cv.hidden=false;tags.forEach(t=>t.hidden=false);cv.dataset.seed=r.dataset.seed;drawThumb(cv,+r.dataset.seed,true);}
  }
  rows.forEach((r,i)=>{r.addEventListener('mouseenter',()=>show(i));r.addEventListener('focus',()=>show(i));});
})();
$$('.case-row').forEach(r=>onHover(r,()=>decode($('.nm',r),360)));

/* ---------- work cards ---------- */
$$('.card').forEach(c=>onHover(c,()=>{
  const cv=$('.thumb canvas[data-seed]',c);if(cv&&!cv._busy&&!RM)drawThumb(cv,seedOf(cv),true);
  decode($('.card-name',c),360);
}));
$$('.pg').forEach(p=>onHover(p,()=>decode($('.h3',p),360)));
$$('.built li').forEach(li=>li.addEventListener('mouseenter',()=>decode($('.h3',li),360)));

/* ---------- checklist strike ---------- */
function tickItem(li,anim){
  li.classList.add('done');$('.b',li).textContent='[x]';
  const by=$('.by',li);by.textContent=li.dataset.by;if(anim)decode(by,360);
}
$$('.check[data-anim]').forEach(list=>{
  if(RM){$$('.ck',list).forEach(li=>tickItem(li,false));return;}
  once([list],async l=>{const items=$$('.ck',l);for(let i=0;i<items.length;i++){await sleep(i?480:160);tickItem(items[i],true);}},.3);
});

/* ---------- log pane ---------- */
function makePane(p,c){
  function summary(){
    if(c.sum)return c.sum;
    const toS=t=>{const q=t.split(':').map(Number);return q[0]*3600+q[1]*60+q[2]};
    let d=toS(c.run[c.run.length-1][0])-toS(c.run[0][0]);if(d<0)d+=86400;
    const actions=c.run.filter(r=>!r[4]).length,ap=c.run.filter(r=>r[4]==='need').length;
    const dur=d>=3600?Math.floor(d/3600)+'h '+pad2(Math.floor(d%3600/60))+'m':Math.floor(d/60)+'m '+pad2(d%60)+'s';
    return 'done in '+dur+' / '+actions+' steps / '+ap+' check'+(ap===1?'':'s')+' with you / no errors';
  }
  function rowEl(r){
    const d=document.createElement('div');d.className='row';
    const eng=/^@[a-z]+$/.test(r[1]),who=WHO[r[1]]||r[1];
    d.innerHTML='<span class="ts">'+esc(r[0])+'</span><span class="ac'+(r[4]?' '+esc(r[4]):'')+(eng?' e-'+r[1].slice(1):'')+(!eng&&!WHO[r[1]]?' ext':'')+'">'+(eng&&BOTS[r[1].slice(1)]?botTag(r[1].slice(1)):'')+esc(who)+'</span><span class="msg">'+esc(r[2])+'</span><span class="res">'+esc(r[3])+'</span>';
    return d;
  }
  function endEl(){const d=document.createElement('div');d.className='end';d.innerHTML='<span class="chip">[ok]</span><span class="s">'+esc(summary())+'</span>';return d;}
  function setState(s,l){p.dataset.state=s;$('.st',p).textContent=l||s;}
  const tx=$('.cmd-tx',p),caret=$('.caret',p),rows=$('.rows',p);
  function finish(){p._run=null;tx.textContent=c.cmd;caret.hidden=true;rows.innerHTML='';c.run.forEach(r=>rows.appendChild(rowEl(r)));rows.appendChild(endEl());setState('complete');}
  function stop(){p._run=null;}
  async function run(){
    if(RM){finish();return;}
    const id={};p._run=id;const alive=()=>p._run===id;
    tx.textContent='';rows.innerHTML='';caret.hidden=false;setState('running');
    for(const ch of c.cmd){if(!alive())return;tx.textContent+=ch;await sleep(c.fast?10+Math.random()*14:16+Math.random()*26);}
    await sleep(c.fast?220:320);if(!alive())return;caret.hidden=true;
    for(const r of c.run){
      if(r[4]==='me'){
        setState('waiting','waiting on '+(WHO[r[1]]||r[1]));
        const w=document.createElement('div');w.className='row wait';
        w.innerHTML='<span class="ts"></span><span class="ac">'+esc(WHO[r[1]]||r[1])+'</span><span class="msg">waiting for your OK</span><span class="res spin">|</span>';
        rows.appendChild(w);
        const sp=$('.spin',w),fr='|/-\\',until=performance.now()+1500;let k=0;
        while(performance.now()<until){await sleep(105);if(!alive())return;sp.textContent=fr[++k%4];}
        w.remove();setState('running');
      }else{
        await sleep((c.fast?420:360)+Math.random()*300);if(!alive())return;
      }
      const el=rowEl(r);rows.appendChild(el);decode($('.res',el),300);
    }
    await sleep(420);if(!alive())return;
    rows.appendChild(endEl());setState('complete');
  }
  return {run,finish,stop,set(n){c=n;}};
}
$$('.pane[data-src]').forEach(p=>{
  const src=document.getElementById(p.dataset.src);if(!src)return;
  let c;try{c=JSON.parse(src.textContent)}catch(e){return;}
  const ctl=makePane(p,c);
  $('.replay',p).addEventListener('click',ctl.run);
  if(RM)ctl.finish();else once([p],ctl.run,.3);
});

/* ---------- job walkthrough sheet ---------- */
$$('[data-jobs]').forEach(list=>{
  const src=document.getElementById(list.dataset.jobs);if(!src)return;
  let J;try{J=JSON.parse(src.textContent)}catch(e){return;}
  let dlg=$('#job-sheet'),ctl=null,opener=null;
  function build(){
    dlg=document.createElement('dialog');dlg.className='sheet';dlg.id='job-sheet';dlg.setAttribute('aria-labelledby','js-t');
    dlg.innerHTML='<div class="sheet-hd"><span class="etags"><span class="etag" id="js-tag"></span></span><span class="label" id="js-trig"></span><button class="sheet-x label" type="button">close &times;</button></div>'
      +'<div class="sheet-bd"><h2 class="sheet-t" id="js-t"></h2><p class="sheet-d" id="js-d"></p>'
      +'<div class="pane" data-state="idle"><div class="pane-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">What happens</span><span class="label">example</span></div>'
      +'<div class="pane-bd"><div class="cmd"><span class="pr">$</span><span class="cmd-tx"></span><span class="caret" aria-hidden="true"></span></div><div class="rows" aria-live="polite"></div></div>'
      +'<div class="pane-ft"><span class="dot" aria-hidden="true"></span><span class="label st">idle</span><button class="replay" type="button">Replay</button></div></div>'
      +'<dl class="sheet-kv"><div><dt class="label">Where you come in</dt><dd id="js-you"></dd></div><div><dt class="label">What you get</dt><dd id="js-get"></dd></div></dl>'
      +'<div class="actions"><a class="btn" id="js-start">Apply</a><a class="btn ghost" id="js-demo">See an example</a></div></div>';
    document.body.appendChild(dlg);
    $('.sheet-x',dlg).addEventListener('click',close);
    dlg.addEventListener('cancel',e=>{e.preventDefault();close();});
    dlg.addEventListener('click',e=>{if(e.target===dlg)close();});
    dlg.addEventListener('close',()=>{if(ctl)ctl.stop();document.documentElement.classList.remove('sheet-open');if(opener&&opener.focus)opener.focus();});
    $('.replay',dlg).addEventListener('click',()=>ctl&&ctl.run());
  }
  function close(){
    if(!dlg||!dlg.open||dlg.classList.contains('is-closing'))return;
    if(RM){dlg.close();return;}
    dlg.classList.add('is-closing');
    setTimeout(()=>{dlg.classList.remove('is-closing');dlg.close();},MS('--panel-close-dur',350));
  }
  function open(i,btn){
    const j=J.jobs[i];if(!j)return;
    if(!dlg)build();
    opener=btn;
    dlg.className='sheet e-'+j.e;
    const tg=$('#js-tag',dlg);tg.className='etag e-'+j.e;tg.textContent=j.name;
    $('#js-trig',dlg).textContent='runs '+j.trig;
    $('#js-t',dlg).textContent=j.title;$('#js-d',dlg).textContent=j.desc;
    $('#js-you',dlg).textContent=j.you;$('#js-get',dlg).textContent=j.get;
    const st=$('#js-start',dlg),dm=$('#js-demo',dlg);
    st.href=J.start;st.innerHTML='Apply <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M2.5 7h9M8 3.5 11.5 7 8 10.5"/></svg>';
    dm.href=J.demo;dm.innerHTML='See an example <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M2.5 7h9M8 3.5 11.5 7 8 10.5"/></svg>';
    const steps=j.steps.filter(r=>!r[4]).length,checks=j.steps.filter(r=>r[4]==='need').length;
    const c={cmd:j.ex,run:j.steps,fast:true,sum:steps+' steps / '+(checks?checks+' check'+(checks===1?'':'s')+' with you':'runs on its own')};
    const pane=$('.pane',dlg);
    if(ctl)ctl.stop();ctl=makePane(pane,c);
    document.documentElement.classList.add('sheet-open');
    if(typeof dlg.showModal==='function')dlg.showModal();else dlg.setAttribute('open','');
    $('.sheet-bd',dlg).scrollTop=0;
    $('.sheet-x',dlg).focus();
    const tt=$('#js-t',dlg);recs.delete(tt);tt.removeAttribute('aria-label');decode(tt,520);
    if(RM)ctl.finish();else ctl.run();
  }
  $$('.play-open',list).forEach(b=>b.addEventListener('click',()=>open(+b.dataset.job,b)));
});

/* ---------- plays filter + engine hovers ---------- */
$$('.filters').forEach(bar=>{
  const list=bar.nextElementSibling;if(!list)return;
  const btns=$$('button[data-f]',bar),items=$$('[data-e]',list);
  btns.forEach(b=>b.addEventListener('click',()=>{
    const f=b.dataset.f;
    btns.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
    let k=0;
    items.forEach(it=>{const on=f==='all'||it.dataset.e===f;it.hidden=!on;if(on&&!RM){const h=$('.h3',it);setTimeout(()=>decode(h,360),k++*50);}});
  }));
  btns.forEach(b=>onHover(b,()=>decode(b,300)));
});
$$('.play').forEach(pl=>pl.addEventListener('mouseenter',()=>decode($('.h3',pl),360)));
$$('.eng,.strip').forEach(e=>e.addEventListener('mouseenter',()=>{decode($('.eng-name,.strip-name',e),420,CAPS+'abcdefghijklmnopqrstuvwxyz');pixDecode($('.px',e),420);}));
$$('.idx a').forEach(a=>a.addEventListener('mouseenter',()=>decode($('.idx-name',a),380,CAPS+'abcdefghijklmnopqrstuvwxyz')));
/* jobs rail arrows */
$$('[data-rail]').forEach(b=>b.addEventListener('click',()=>{const r=$('.plays.rail');if(r)r.scrollBy({left:(+b.dataset.rail)*Math.max(280,r.clientWidth*.8),behavior:RM?'auto':'smooth'});}));

/* ---------- the site mock: the price slider moves like someone's using it ---------- */
(function(){
  if(RM)return;
  $$('.site-mock').forEach(m=>{
    const k=$('.sm-sl i',m),amt=$('[data-sm-amt]',m);if(!k||!amt)return;
    const stops=[[18,640],[40,1240],[64,1980],[82,2560],[52,1610]];let i=0,on=false;
    once([m],()=>{on=true;},.2);
    setInterval(()=>{if(!on||document.hidden)return;i=(i+1)%stops.length;const [p,v]=stops[i];k.style.left=p+'%';
      setTimeout(()=>{amt.textContent=v.toLocaleString('en-US');decode(amt,300);},350);},2200);
  });
})();

/* ---------- tools board: pick an industry, see what plugs into each engine ---------- */
(function(){
  const sel=$('#tool-for'),board=$('#tboard'),src=$('#tools-data'),go=$('#tool-go');if(!sel||!board||!src)return;
  let D;try{D=JSON.parse(src.textContent)}catch(e){return;}
  const cols=$$('.tcol',board);
  sel.addEventListener('change',()=>{
    const x=D[sel.value];if(!x)return;
    cols.forEach(c=>{
      const k=([...c.classList].find(z=>z.indexOf('e-')===0)||'e-').slice(2),u=x.u.indexOf(k)>-1;
      c.classList.toggle('usual',u);$('.tcol-st',c).textContent=u?'usually first':'add any time';
      $('.tlist',c).innerHTML=(x.t[k]||[]).map(([n,d])=>'<li class="tl"><div class="tool-in"><span class="label tl-k">+ tool</span><b class="tl-n">'+esc(n)+'</b><span class="tl-d">'+esc(d)+'</span></div></li>').join('');
      if(!RM)$$('.tl-n',c).forEach((el,i)=>setTimeout(()=>decode(el,380),i*60));
    });
    if(go){go.href='for/'+sel.value+'.html#tools';if(go.firstChild&&go.firstChild.nodeType===3)go.firstChild.nodeValue='Open the '+x.n.toLowerCase()+' page ';}
  });
})();

/* ---------- sound familiar: card carousel ---------- */
(function(){
  const rail=$('.say-rail');if(!rail)return;
  const cards=$$('.say-card',rail),segs=$$('.say-meter i'),num=$('.say-n b'),n=cards.length;if(!n)return;
  const step=()=>cards[0].getBoundingClientRect().width+(parseFloat(getComputedStyle(rail).columnGap)||14);
  const max=()=>rail.scrollWidth-rail.clientWidth;
  const at=()=>rail.scrollLeft>=max()-4?n-1:Math.round(rail.scrollLeft/step());
  const go=i=>rail.scrollTo({left:Math.min(((i%n)+n)%n*step(),max()),behavior:RM?'auto':'smooth'});
  let shown=-1;
  function sync(){const i=at();if(i===shown)return;shown=i;segs.forEach((s,k)=>s.classList.toggle('on',k===i));if(num)num.textContent=pad2(i+1);}
  let raf=0;rail.addEventListener('scroll',()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(sync);},{passive:true});
  sync();
  // autoplay until someone takes over, then it stays where they leave it
  let stopped=RM,hover=false,timer=null;
  const stop=()=>{stopped=true;clearInterval(timer);};
  $$('[data-say]').forEach(b=>b.addEventListener('click',()=>{stop();go(at()+(+b.dataset.say));}));
  ['wheel','touchstart','keydown'].forEach(ev=>rail.addEventListener(ev,stop,{passive:true}));
  rail.addEventListener('mouseenter',()=>{hover=true;});rail.addEventListener('mouseleave',()=>{hover=false;});
  // drag sideways with a mouse
  let drag=null,moved=false;
  rail.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.button!==0)return;stop();drag={x:e.clientX,l:rail.scrollLeft};moved=false;rail.classList.add('dragging');});
  addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.x;if(Math.abs(dx)>4)moved=true;rail.scrollLeft=drag.l-dx;});
  addEventListener('pointerup',()=>{if(!drag)return;drag=null;rail.classList.remove('dragging');if(moved)go(at());});
  rail.addEventListener('click',e=>{if(moved){e.preventDefault();e.stopPropagation();moved=false;}},true);
  if(!RM)once([rail],()=>{timer=setInterval(()=>{if(stopped||hover||document.hidden)return;go(at()+1>=n?0:at()+1);},4200);},.4);
})();
/* overnight clock follows the log */
(function(){const clk=$('#night-clock'),rows=$('.pane[data-src="night-data"] .rows');if(!clk||!rows||!('MutationObserver' in window))return;
  new MutationObserver(()=>{const ts=$$('.row .ts',rows).map(t=>t.textContent).filter(Boolean).pop();if(ts)clk.textContent=ts.slice(0,5);}).observe(rows,{childList:true});})();
if(!RM)once([$('.engines'),$('.strips')],el=>$$('.px',el).forEach((svg,i)=>setTimeout(()=>pixDecode(svg,900),i*160)));

/* ---------- ticker ---------- */
(function(){
  const track=$('#tk-track'),set=track&&$('.tk-set',track);if(!set)return;
  const base=Array.from(set.children).map(n=>n.cloneNode(true));let guard=0;
  while(set.scrollWidth<innerWidth+200&&guard++<6)base.forEach(n=>set.appendChild(n.cloneNode(true)));
  track.appendChild(set.cloneNode(true));
})();

/* ---------- copy email ---------- */
(function(){
  const b=$('#copy'),addr=$('#addr'),st=$('#copied');if(!b||!addr)return;
  b.addEventListener('click',()=>{
    const t=addr.textContent.trim();
    const fail=()=>{try{const r=document.createRange();r.selectNodeContents(addr);const s=getSelection();s.removeAllRanges();s.addRange(r);}catch(e){}if(st)st.textContent='Selected. Copy it from here.';};
    try{navigator.clipboard.writeText(t).then(()=>{if(st)st.textContent='Copied';},fail);}catch(e){fail();}
  });
})();

/* ---------- phone menu ---------- */
(function(){
  const btn=$('#menu-btn'),menu=$('#menu');if(!btn||!menu)return;
  const t=$('.mb-t',btn),wide=matchMedia('(min-width:1000px)');
  function set(open){
    btn.setAttribute('aria-expanded',String(open));t.textContent=open?'Close':'Menu';
    menu.hidden=!open;document.documentElement.classList.toggle('menu-open',open);
    if(open)$$('.mt',menu).forEach((el,i)=>setTimeout(()=>decode(el,420),i*70));
  }
  btn.addEventListener('click',()=>set(btn.getAttribute('aria-expanded')!=='true'));
  menu.addEventListener('click',e=>{if(e.target.closest('a'))set(false);});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!menu.hidden){set(false);btn.focus();}});
  const close=e=>{if(e.matches)set(false);};
  wide.addEventListener?wide.addEventListener('change',close):wide.addListener(close);
})();

/* ---------- mega menu: who it's for ---------- */
(function(){
  const btn=$('#mega-btn'),mg=$('#mega');if(!btn||!mg)return;
  const fine=matchMedia('(hover:hover) and (pointer:fine)');
  let t=null,openedAt=0,isOpen=false,shut=null;
  function set(open){
    clearTimeout(t);
    if(open===isOpen)return;
    isOpen=open;btn.setAttribute('aria-expanded',String(open));clearTimeout(shut);
    if(open){
      mg.hidden=false;mg.classList.remove('is-closing');void mg.offsetWidth;mg.classList.add('is-open');
      openedAt=performance.now();$$('.mg-g',mg).forEach((el,i)=>setTimeout(()=>decode(el,300),i*50));
    }else{
      mg.classList.remove('is-open');mg.classList.add('is-closing');
      shut=setTimeout(()=>{mg.classList.remove('is-closing');mg.hidden=true;},RM?0:MS('--dropdown-close-dur',150));
    }
  }
  btn.addEventListener('click',()=>{if(isOpen&&fine.matches&&performance.now()-openedAt<600)return;set(!isOpen);});
  [btn,mg].forEach(el=>{
    el.addEventListener('mouseenter',()=>{if(!fine.matches)return;clearTimeout(t);t=setTimeout(()=>set(true),80);});
    el.addEventListener('mouseleave',()=>{if(!fine.matches)return;clearTimeout(t);t=setTimeout(()=>set(false),240);});
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&isOpen){set(false);btn.focus();}});
  document.addEventListener('click',e=>{if(isOpen&&!mg.contains(e.target)&&!btn.contains(e.target))set(false);});
  mg.addEventListener('focusout',e=>{const to=e.relatedTarget;if(to&&!mg.contains(to)&&to!==btn)set(false);});
  $$('.mg-col li a',mg).forEach(a=>onHover(a,()=>decode($('.mg-n',a),280)));
})();
(function(){
  const b=$('.menu-sub-btn'),p=$('#menu-for');if(!b||!p)return;
  b.addEventListener('click',()=>{const o=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(o));p.hidden=!o;});
})();

/* ---------- built-for picker ---------- */
$$('[data-tabs]').forEach(root=>{
  const tabs=$$('[role="tab"]',root),panels=tabs.map(t=>document.getElementById(t.getAttribute('aria-controls')));
  function sel(i,focus){
    tabs.forEach((t,k)=>{const on=k===i;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;if(panels[k])panels[k].hidden=!on;});
    if(focus)tabs[i].focus();
    const p=panels[i];if(!p)return;
    $$('.mini canvas[data-seed]',p).forEach(cv=>drawMini(cv,seedOf(cv)));
    decode($('.fp-name',p),420);
  }
  tabs.forEach((t,i)=>{
    t.addEventListener('click',()=>sel(i,false));
    t.addEventListener('keydown',e=>{
      let j=null;
      if(e.key==='ArrowRight')j=(i+1)%tabs.length;
      else if(e.key==='ArrowLeft')j=(i-1+tabs.length)%tabs.length;
      else if(e.key==='Home')j=0;
      else if(e.key==='End')j=tabs.length-1;
      if(j!==null){e.preventDefault();sel(j,true);}
    });
    onHover(t,()=>decode(t,300));
  });
});
$$('.mcell').forEach(c=>c.addEventListener('mouseenter',()=>decode($('.h3',c),360)));

/* ---------- inquiry form ---------- */
$$('form.inq').forEach(f=>{
  const st=$('.inq-status',f),btn=$('button[type="submit"]',f),KEY='oplev-inquiry',TEXT=['name','email','company','message'];
  const MAIL=f.dataset.email||'';
  const PRE={one:'license-one',core:'license-core',company:'license-company',resale:'resale-yes'};
  const h=(location.hash||'').slice(1).toLowerCase();
  if(h){const el=document.getElementById('inq-'+(PRE[h]||('type-'+h)));if(el&&f.contains(el))el.checked=true;}
  try{const d=JSON.parse(localStorage.getItem(KEY)||'{}');TEXT.forEach(k=>{const el=f.elements[k];if(el&&d[k]&&!el.value)el.value=d[k];});}catch(e){}
  // marketplace links (start.html#os-practice) say which OS the inquiry is about
  const osBox=$('.inq-os',f),osIn=$('#inq-os',f);let osNames={};try{osNames=JSON.parse(($('.os-names',f)||{}).textContent||'{}')}catch(e){}
  function setOS(id){
    if(!osBox)return;const nm=id&&osNames[id];
    osBox.hidden=!nm;osIn.disabled=!nm;osIn.value=nm||'';$('.inq-os-n',osBox).textContent=nm||'';
  }
  if(h.indexOf('os-')===0)setOS(h.slice(3));
  // a build from the home walkthrough (start.html#build=...)
  const bBox=$('.inq-build',f),raw=location.hash||'';
  if(bBox&&raw.indexOf('#build=')===0){
    let B=null;try{B=JSON.parse(decodeURIComponent(raw.slice(7)));}catch(e){}
    if(B&&B.b){
      const N={leads:'Leads',agents:'Agents',ops:'Ops',marketing:'Marketing'},eng=(B.e||[]).filter(k=>N[k]);
      const txt=B.b+' / '+eng.map(k=>N[k]).join(', ')+(B.t&&B.t.length?' / add-ons: '+B.t.join(', '):'')+(B.s?' / '+B.s+' style':'');
      const inp=$('input',bBox);inp.value=txt.slice(0,600);inp.disabled=false;$('.inq-os-n',bBox).textContent=txt;bBox.hidden=false;
      const ty=document.getElementById('inq-type-'+B.f);if(ty&&f.contains(ty))ty.checked=true;
      eng.forEach(k=>{const c=document.getElementById('inq-build-'+k);if(c)c.checked=true;});
      const lic=document.getElementById('inq-license-'+(eng.length>=3?'company':eng.length===2?'core':'one'));if(lic)lic.checked=true;
      $('.inq-os-x',bBox).addEventListener('click',()=>{bBox.hidden=true;inp.disabled=true;inp.value='';});
    }
  }
  if(osBox)$('.inq-os-x',osBox).addEventListener('click',()=>{setOS(null);const m=f.elements.message;if(m)m.focus();});
  const other=$('.type-other',f),otherIn=other&&$('input',other);
  function syncOther(focus){
    if(!other)return;const r=f.querySelector('input[name="type"]:checked'),on=!!(r&&r.id==='inq-type-other');
    other.hidden=!on;otherIn.disabled=!on;
    if(on&&focus)otherIn.focus();
  }
  $$('input[name="type"]',f).forEach(r=>r.addEventListener('change',()=>syncOther(true)));
  syncOther(false);
  f.addEventListener('input',e=>{
    try{const d={};TEXT.forEach(k=>d[k]=f.elements[k].value);localStorage.setItem(KEY,JSON.stringify(d));}catch(err){}
    const fl=e.target.closest&&e.target.closest('.fl.bad');if(fl){fl.classList.remove('bad');e.target.removeAttribute('aria-invalid');}
  });
  const RULES=[['name',v=>v.trim().length>0],['email',v=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim())],['message',v=>v.trim().length>0]];
  function check(){
    let first=null;
    RULES.forEach(([k,ok])=>{
      const el=f.elements[k],fl=el.closest('.fl'),good=ok(el.value);
      fl.classList.toggle('bad',!good);
      if(good)el.removeAttribute('aria-invalid');else{el.setAttribute('aria-invalid','true');shake(el);if(!first)first=el;}
    });
    return first;
  }
  function out(lines){
    st.hidden=false;st.innerHTML='';
    lines.forEach((l,i)=>{const s=document.createElement('span');s.className='ln';s.style.animationDelay=(i*140)+'ms';s.innerHTML=l;st.appendChild(s);});
  }
  function collect(){
    const d={};new FormData(f).forEach((v,k)=>{if(k==='build'){(d.build=d.build||[]).push(v);}else d[k]=v;});
    return d;
  }
  function compose(d){
    const rows=[['Name',d.name],['Email',d.email],['Company',d.company],['Asking about',d.os],['Their build',d.setup],['Business',d.type_other||d.type],['Team size',d.team],
      ['Build',(d.build||[]).join(', ')],['License',d.license],['Sell to others',d.resale],['Start',d.timing]];
    return rows.filter(r=>r[1]).map(r=>r[0]+': '+r[1]).join('\n')+'\n\nWhat still runs through me:\n'+(d.message||'');
  }
  function fallback(d){
    const text=compose(d);
    out(['<span class="chip">[!]</span> this form can\'t send from here yet.','  email it to <b>'+esc(MAIL)+'</b> and we\'ll take it from there. your application is ready to copy:']);
    const pre=document.createElement('pre');pre.textContent=text;st.appendChild(pre);
    const b=document.createElement('button');b.type='button';b.className='btn ghost btn-sm';b.textContent='Copy note';
    b.addEventListener('click',()=>{
      const sel=()=>{try{const r=document.createRange();r.selectNodeContents(pre);const s=getSelection();s.removeAllRanges();s.addRange(r);}catch(e){}b.textContent='Selected. Copy it';};
      try{navigator.clipboard.writeText(MAIL?('To: '+MAIL+'\n\n'+text):text).then(()=>{b.textContent='Copied';},sel);}catch(e){sel();}
    });
    st.appendChild(b);
  }
  f.addEventListener('submit',async e=>{
    e.preventDefault();
    const bad=check();
    if(bad){out(['<span class="chip">[!]</span> add your name, a valid email and what still runs through you.']);bad.focus();return;}
    const d=collect(),first=esc((d.name||'').trim().split(/\s+/)[0]||'there');
    btn.disabled=true;
    out(['> sending application ...']);
    let ok=false,code=0,msg='';
    try{
      const r=await fetch(f.getAttribute('action'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
      code=r.status;const j=await r.json().catch(()=>({}));ok=r.ok&&j.ok===true;msg=j.error||'';
    }catch(err){}
    btn.disabled=false;
    if(ok){
      out(['> sending application ... <b>ok</b>','  received ............ <b>ok</b>','  read by ............. <b>andre + matt</b>','<span class="chip">[ok]</span> thanks, '+first+'. we review every application and reply personally.']);
      f.reset();try{localStorage.removeItem(KEY);}catch(err){}
    }else if(code===400&&msg){
      out(['<span class="chip">[!]</span> '+esc(msg)]);
    }else{
      fallback(d);
    }
  });
});

/* ---------- faq: accordion ---------- */
$$('.faq .t-acc').forEach(acc=>{
  const h=$('.t-acc-head',acc),panel=$('.t-acc-panel',acc);if(!h||!panel)return;
  h.addEventListener('click',()=>{const o=acc.dataset.open!=='true';acc.dataset.open=String(o);h.setAttribute('aria-expanded',String(o));panel.inert=!o;});
});

/* ---------- hover + scroll decodes ---------- */
$$('.links a,.links-btn,.btn').forEach(el=>onHover(el,()=>decode(el,360)));
onHover($('.nav .brand'),()=>decode($('.brand-t'),360,CAPS));
$$('.plan').forEach(p=>p.addEventListener('mouseenter',()=>decode($('.h3',p),360)));
$$('.ev').forEach(p=>p.addEventListener('mouseenter',()=>decode($('.h3',p),360)));
if(!RM){
  once($$('.h2'),el=>decode(el));
  once([$('.plans')],el=>$$('.amt',el).forEach((a,i)=>setTimeout(()=>decode(a,700),i*160)),.3);
}

/* ---------- the characters come alive ---------- */
$$('.bot-xs[data-bot]').forEach(el=>{el.innerHTML=botSVG(el.dataset.bot,null,true);});
$$('.bot-card').forEach(card=>{
  const bots=$$('.bot[data-bot]',card),say=$('.bot-say',card);if(!bots.length)return;
  const name=bots[0].dataset.bot,B=BOTS[name],lines=BOT_LINES[name]||[''];let li=0,busy=false;
  const cols=Math.max.apply(null,B.base.map(r=>r.length)),crew=bots.length>1;
  bots.forEach((el,i)=>{el.style.width=(cols*(crew?(i===1?5:4):7))+'px';});
  const draw=(el,over)=>{el.innerHTML=botSVG(name,over);};
  bots.forEach(el=>draw(el));
  const speak=()=>{redecode(say,lines[li%lines.length],420);li++;};
  if(RM){say.textContent=lines[0];li=1;}else once([card],speak,.4);
  // idle: each one blinks and fidgets on its own clock
  if(!RM)bots.forEach(el=>{(function loop(){setTimeout(async()=>{
    if(!busy){
      if(B.idle&&Math.random()<(name==='leads'?.8:.5)){const f=B.idle;for(let k=0;k<(name==='ops'?3:6);k++){if(busy)break;draw(el,f[k%f.length]);await sleep(name==='ops'?260:140);}if(!busy)draw(el);}
      else{draw(el,B.blink);await sleep(140);if(!busy)draw(el);}
    }
    loop();},(name==='leads'?900:1800)+Math.random()*3400);})();});
  async function act(){
    if(busy)return;busy=true;speak();
    if(RM){busy=false;return;}
    const A=B.act;
    if(crew){
      bots.forEach((el,i)=>setTimeout(()=>{el.classList.add('hop');draw(el,A[0]);setTimeout(()=>{el.classList.remove('hop');draw(el);},300);},i*110));
      await sleep(660);
    }else{
      if(B.hop)bots.forEach(el=>el.classList.add('hop'));
      for(let i=0;i<(B.actN||4);i++){bots.forEach(el=>draw(el,A[i%A.length]));await sleep(B.actMs||160);if(i===1&&B.hop)bots.forEach(el=>el.classList.remove('hop'));}
      bots.forEach(el=>{el.classList.remove('hop');draw(el);});
    }
    busy=false;
  }
  card.addEventListener('click',act);
  card.addEventListener('mouseenter',act);
});

/* ---------- footer wordmark: every tile is its own pixel. Hover one to color it. ---------- */
(function(){
  const wm=$('#wm'),svg=$('#wm-t');if(!wm||!svg)return;
  const L=$$('.wm-l',svg),T=$$('.t',svg);if(!T.length)return;
  const COLS=['var(--ops)','var(--agents)','var(--leads)','var(--marketing)'];
  const BLINK=[{opacity:.1},{opacity:1},{opacity:.2},{opacity:1}];
  const blink=(t,ms)=>{if(!RM&&t.animate)t.animate(BLINK,{duration:ms||220,easing:'steps(4,end)'});};
  T.forEach(t=>{t._c=-1;});
  // -1 is paper; any other number is an engine color
  function paint(t,c){if(c===t._c)return;t._c=c;t.style.fill=c<0?'':COLS[c];blink(t);}
  function pick(t){let c;do{c=Math.random()*COLS.length|0;}while(c===t._c);return c;}
  let idle=null;
  function rest(){clearTimeout(idle);idle=setTimeout(()=>T.forEach(t=>{if(t._c>=0)setTimeout(()=>paint(t,-1),Math.random()*800);}),6000);}
  T.forEach(t=>t.addEventListener('pointerenter',e=>{if(e.pointerType==='touch')return;paint(t,pick(t));rest();}));
  // on a phone, tap a tile to color it
  let tapped=false;
  svg.addEventListener('pointerdown',e=>{if(e.pointerType!=='touch')return;const t=e.target.closest&&e.target.closest('.t');tapped=!!t;if(t){paint(t,pick(t));rest();}});
  // click anywhere else on the wordmark: a wave of color, one letter at a time
  wm.addEventListener('click',e=>{
    if(tapped){tapped=false;return;}
    L.forEach((g,i)=>{const c=Math.random()*COLS.length|0;$$('.t',g).forEach(t=>setTimeout(()=>paint(t,c),i*80+Math.random()*240));});rest();
  });
  // first time it scrolls into view, the tiles switch on in random order
  if(!RM&&hasIO){
    svg.classList.add('boot');
    once([wm],()=>{T.forEach(t=>{t.style.opacity='0';setTimeout(()=>{t.style.opacity='';blink(t,200);},80+Math.random()*900);});svg.classList.remove('boot');},.15);
  }
})();

let rz;addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>{drawAllMinis();refreshThumbs(false);},150);});
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>refreshThumbs(true));

/* ---------- build your engine: the home walkthrough ---------- */
(function(){
  const root=$('[data-bx]');if(!root)return;
  let D;try{D=JSON.parse($('#bx-data',root).textContent);}catch(e){return;}
  const ORDER=['leads','agents','ops','marketing'],KEY='oplev-build';
  const sel=$('#bx-biz',root),toolsEl=$('#bx-tools',root),rowsEl=$('[data-bx-rows]',root),doneEl=$('[data-bx-done]',root);
  const playBtn=$('[data-bx-play]',root);
  const S={biz:sel.value,eng:[],tools:new Set(),style:'clean'};
  const tk=(k,n)=>k+'|'+n;
  const price=n=>n>=3?'$15k+':n===2?'$10k':'$5k';
  const plural=(n,w)=>n+' '+w+(n===1?'':'s');
  const ICP=()=>D.icps[S.biz];
  function firstTools(k){
    const list=(ICP().t[k]||[]);let picked=list.filter(t=>t[2]);
    if(!picked.length&&list.length)picked=[list[0]];
    picked.forEach(t=>S.tools.add(tk(k,t[0])));
  }
  function defaults(id){S.biz=id;S.eng=ICP().e.slice();S.tools=new Set();S.eng.forEach(firstTools);}
  // pick up where this visitor left off
  let saved=null;try{saved=JSON.parse(localStorage.getItem(KEY)||'null');}catch(e){}
  if(saved&&D.icps[saved.biz]){
    S.biz=saved.biz;sel.value=saved.biz;
    S.eng=(saved.eng||[]).filter(k=>ORDER.includes(k));if(!S.eng.length)S.eng=ICP().e.slice();
    const valid=new Set();S.eng.forEach(k=>(ICP().t[k]||[]).forEach(t=>valid.add(tk(k,t[0]))));
    S.tools=new Set((saved.tools||[]).filter(t=>valid.has(t)));
    if(D.styles[saved.style])S.style=saved.style;
  }else defaults(sel.value);

  /* website mock: restyles with the build style, shows the add-ons that live on the site */
  const KINDS=[[/price|quote|estimate|calculat|scoper|value|ballpark|cost/,'calc'],[/finder|quiz|matcher|qualifier|fit check|preview|shade/,'quiz'],[/\bform\b/,'form'],
    [/book|consult|discovery|demo|trial|tour|evaluation|showing/,'slots'],[/newsletter|series|signup|\blist\b|offer|welcome|waitlist|campaign|email|pass|guide|challenge|alert/,'sign'],
    [/form|request|intake|application|referral/,'form'],[/repl|answer|question|line|routing/,'chat']];
  const kindOf=n=>{n=n.toLowerCase();for(const [re,k] of KINDS)if(re.test(n))return k;return 'form';};
  // follow-ups and tests run behind the scenes, everything else shows up on the website
  const onSite=(k,n)=>(k==='leads'||k==='marketing')&&!/follow-up|page test|tests$/i.test(n);
  function siteTools(){
    const out=[];['leads','marketing'].forEach(k=>{if(!S.eng.includes(k))return;(ICP().t[k]||[]).forEach(t=>{if(S.tools.has(tk(k,t[0]))&&onSite(k,t[0]))out.push([k,t[0]]);});});
    return out;
  }
  function widget(k,name){
    const kd=kindOf(name),l='<span class="bm-wl">'+esc(name)+'</span>',a=' data-w="'+esc(tk(k,name))+'"';
    const inner={calc:l+'<span class="bm-sl"><i></i></span><b class="bm-amt">$1,240</b>',
      quiz:l+'<span class="bm-q">Which one fits you?</span><span class="bm-chips"><i></i><i></i><i></i></span>',
      slots:l+'<span class="bm-chips t"><i>9:00</i><i>11:30</i><i>2:15</i></span>',
      sign:l+'<span class="bm-in"></span><em>Join</em>',
      form:l+'<span class="bm-in"></span><span class="bm-in s"></span><em>Send</em>',
      chat:l+'<span class="bm-bub">Hi! How can we help?</span>'}[kd];
    return '<div class="bm-w w-'+kd+' e-'+k+'"'+a+'>'+inner+'</div>';
  }
  function mock(){
    const c=ICP().site,dom=c[0].toLowerCase().replace(/[^a-z0-9]/g,'')+'.com';
    let w=siteTools().slice(0,2).map(t=>widget(t[0],t[1])).join('');
    if(!w)w='<div class="bm-w w-form"><span class="bm-wl">Talk to us</span><span class="bm-in"></span><span class="bm-in s"></span><em>Send</em></div>';
    return '<figure class="bm st-'+S.style+'" aria-label="'+esc(D.styles[S.style]+' website preview for '+c[0])+'">'+
      '<div class="bm-bar"><i></i><i></i><i></i><span>'+esc(dom)+'</span></div>'+
      '<div class="bm-page"><div class="bm-nav"><b>'+esc(c[0])+'</b><span class="bm-links"><i></i><i></i><i></i></span><em>'+esc(c[2])+'</em></div>'+
      '<div class="bm-hero"><p class="bm-h">'+esc(c[1])+'</p><p class="bm-p"></p><p class="bm-p s"></p><span class="bm-btn">'+esc(c[2])+'</span></div>'+
      '<div class="bm-row">'+w+'</div></div><div class="bm-toast t-toast" data-bm-toast aria-hidden="true"></div></figure>';
  }

  /* step 2: add-ons, one column per engine */
  function renderTools(){
    toolsEl.innerHTML=ORDER.map(k=>{
      const on=S.eng.includes(k),e=D.eng[k],list=ICP().t[k]||[];
      const hd='<div class="bx-col-hd">'+botTag(k)+'<b>'+esc(e.n)+'</b><span class="label">'+esc(e.el.toLowerCase())+'</span></div>';
      if(!on)return '<div class="bx-col off e-'+k+'">'+hd+'<p class="bx-off-p">Not in your base yet.</p><button class="bx-add" type="button" data-add="'+k+'">Add '+esc(e.n)+' <span aria-hidden="true">+</span></button></div>';
      if(!list.length)return '<div class="bx-col e-'+k+'">'+hd+'<p class="bx-off-p">We build these to order.</p></div>';
      return '<div class="bx-col e-'+k+'">'+hd+'<ul class="bx-tl">'+list.map(t=>{
        const p=S.tools.has(tk(k,t[0]));
        return '<li><button class="bx-tool" type="button" data-tool="'+esc(tk(k,t[0]))+'" aria-pressed="'+p+'"><span class="bx-tool-top"><b>'+esc(t[0])+'</b><span class="bx-check t-check" aria-hidden="true"><svg viewBox="0 0 10.1668 10.1668"><path d="M1 5.52L3.92 9.17L9.17 1"/></svg></span></span><span class="bx-tool-d">'+esc(t[1])+'</span>'+(t[2]?'<span class="label bx-pop">most picked</span>':'')+'</button></li>';
      }).join('')+'</ul></div>';
    }).join('');
  }

  function summary(){
    const tools=[];ORDER.forEach(k=>{if(!S.eng.includes(k))return;(ICP().t[k]||[]).forEach(t=>{if(S.tools.has(tk(k,t[0])))tools.push(t[0]);});});
    return {b:ICP().n,f:ICP().f,e:S.eng.slice(),t:tools,s:D.styles[S.style]};
  }
  let first=true;
  function sync(){
    const n=S.eng.length,tc=summary().t.length,q=first;first=false;
    $$('.bx-eng',root).forEach(b=>b.setAttribute('aria-pressed',S.eng.includes(b.dataset.eng)?'true':'false'));
    $$('[data-bx-count]',root).forEach(el=>softSwap(el,plural(n,'engine'),q));
    $$('[data-bx-price]',root).forEach(el=>setDigits(el,price(n),q));
    $$('.bx-meter i',root).forEach((el,i)=>el.classList.toggle('on',i<n));
    $$('[data-bx-tcount]',root).forEach(el=>softSwap(el,plural(tc,'add-on'),q));
    $$('[data-bx-biz]',root).forEach(el=>softSwap(el,ICP().n,q));
    const names=ORDER.filter(k=>S.eng.includes(k)).map(k=>D.eng[k].n).join(', ');
    $$('[data-bx-meta]',root).forEach(el=>softSwap(el,names+' / '+plural(tc,'add-on')+' / '+D.styles[S.style],q));
    if(!running)thinkSwap(thinkBox,'a day at '+ICP().site[0].toLowerCase());
    const href='start.html#build='+encodeURIComponent(JSON.stringify(summary()));
    $$('[data-bx-apply]',root).forEach(a=>a.setAttribute('href',href));
    $$('input[name="bx-style"]',root).forEach(r=>{r.checked=r.value===S.style;});
    if(genRun){genRun.cancel();genRun=null;}
    $$('[data-bx-mock]',root).forEach(el=>el.innerHTML=mock());
    try{localStorage.setItem(KEY,JSON.stringify({biz:S.biz,eng:S.eng,tools:Array.from(S.tools),style:S.style}));}catch(e){}
  }
  function changed(){renderTools();sync();stale();}

  sel.addEventListener('change',()=>{defaults(sel.value);changed();});
  $$('.bx-eng',root).forEach(b=>b.addEventListener('click',()=>{
    const k=b.dataset.eng,on=S.eng.includes(k);
    if(on){
      if(S.eng.length===1){
        shake(b);const tw=$('.bx-total',root);tw.classList.add('is-error');clearTimeout(tw._rv);
        tw._rv=setTimeout(()=>tw.classList.remove('is-error'),MS('--revert-hold',3000));return;
      }
      S.eng=S.eng.filter(x=>x!==k);Array.from(S.tools).forEach(t=>{if(t.indexOf(k+'|')===0)S.tools.delete(t);});
    }else{S.eng=ORDER.filter(x=>x===k||S.eng.includes(x));firstTools(k);}
    changed();
  }));
  toolsEl.addEventListener('click',e=>{
    const t=e.target.closest('[data-tool]'),a=e.target.closest('[data-add]');
    if(t){const v=t.dataset.tool;if(S.tools.has(v))S.tools.delete(v);else S.tools.add(v);t.setAttribute('aria-pressed',S.tools.has(v)?'true':'false');sync();stale();}
    else if(a){const k=a.dataset.add;S.eng=ORDER.filter(x=>x===k||S.eng.includes(x));firstTools(k);changed();
      const b=$('[data-tool^="'+k+'|"]',toolsEl);if(b)b.focus();}
  });
  $$('input[name="bx-style"]',root).forEach(r=>r.addEventListener('change',()=>{if(r.checked){S.style=r.value;sync();build();}}));
  // step 3: the preview is drawn as a dotted wireframe, then revealed (transitions.dev UI generation)
  let genRun=null,seen3=false;
  function build(){
    const f=$('[data-bx-mock="style"] .bm',root);if(!f||RM||typeof window.OPGEN!=='function')return;
    if(genRun)genRun.cancel();
    try{genRun=window.OPGEN(f,{duration:1800,maxParts:28,keys:3});}catch(e){genRun=null;}
  }
  const prev3=$('[data-bx-mock="style"]',root);
  if(prev3)once([prev3],()=>{seen3=true;build();},.5);
  addEventListener('opgen',()=>{if(seen3)build();});

  /* step 4: one day, run by the engine */
  const BASE={
    ops:[[360,'ops','Morning summary sent to your phone','What happened overnight and what needs you today.','sent'],[1050,'ops',"Today's numbers updated",'Sales, open jobs and money in, without a spreadsheet.','updated']],
    leads:[[612,'leads','New question on your website','Answered in 2 minutes, with a link to book.','answered','chat'],[1241,'leads','New lead at 8:41pm','Answered on the spot and saved with the whole conversation.','saved','chat']],
    agents:[[614,'agents','Reply drafted in your voice','For the 10:12 question. Waiting for your OK.','needs you',null,1],[619,'you','You approved it from your phone','Sent with a link to book.','approved'],[840,'agents','Reminders sent for tomorrow','Everyone on the schedule, in your voice.','sent']],
    marketing:[[750,'marketing','New subscriber from your website','Welcome email 1 is on its way.','added','sign'],[962,'marketing','Newsletter draft ready','Built from your brand kit. Waiting for your OK.','needs you',null,1],[966,'you','You approved the newsletter','It goes out Tuesday at 9am, from your own domain.','approved']]
  };
  const SLOTS={ops:[365,455,720,1090,1110],agents:[510,585,680,810,915,1000,1145,1200],leads:[545,710,790,1170,1275,1350,1380],marketing:[435,765,930,1130,1160]};
  function events(){
    const ev=[];
    ORDER.forEach(k=>{
      if(!S.eng.includes(k))return;
      BASE[k].forEach(b=>ev.push({m:b[0],k:b[1],t:b[2],d:b[3],st:b[4],site:b[5]||null,need:!!b[6]}));
      let i=0;(ICP().t[k]||[]).forEach(t=>{
        if(!S.tools.has(tk(k,t[0])))return;
        const m=SLOTS[k][i%SLOTS[k].length]+Math.floor(i/SLOTS[k].length)*7;i++;
        const site=onSite(k,t[0])?kindOf(t[0]):null;
        ev.push({m,k,t:t[0],d:t[1],st:'done',site,w:site?tk(k,t[0]):null});
      });
    });
    return ev.sort((a,b)=>a.m-b.m);
  }
  const clock=m=>{const h=Math.floor(m/60)%24,mm=m%60;return ((h%12)||12)+':'+pad2(mm)+(h<12?'am':'pm');};
  const TOAST={calc:'New price request: $1,240',quiz:'Someone found their match',slots:'New booking: Thursday at 11:30',sign:'New subscriber joined',form:'New request came in',chat:'New question: "Any openings this week?"'};
  function rowHTML(ev){
    const who=ev.k==='you'?'<span class="bx-you">You</span>':botTag(ev.k),L=n=>' t-stagger-line t-stagger-line--'+n;
    return '<li class="bx-row t-stagger'+(ev.k==='you'?' is-you':' e-'+ev.k)+(ev.need?' is-need':'')+'"><span class="bx-t'+L(1)+'">'+clock(ev.m)+'</span><span class="bx-who'+L(1)+'">'+who+'</span>'+
      '<span class="bx-txt"><b class="'+L(2).trim()+'">'+esc(ev.t)+'</b><span class="'+L(3).trim()+'">'+esc(ev.d)+'</span></span><span class="bx-st label'+L(4)+'">'+esc(ev.st)+'</span></li>';
  }
  const thinkBox=$('.bx-status .t-think',root),mx=$('.bx-status .t-matrix',root);if(mx)matrix(mx);
  let running=false;
  function setRunning(on){running=on;if(thinkBox)thinkBox.classList.toggle('is-still',!on);if(mx)mx.classList.toggle('is-still',!on);}
  function showDone(on){
    if(on){doneEl.hidden=false;void doneEl.offsetWidth;doneEl.dataset.open='true';}
    else{doneEl.dataset.open='false';doneEl.hidden=true;}
  }
  let run=0,played=false,dirty=false;
  const setStat=(sel2,v,q)=>{const el=$(sel2,root);if(el)setDigits(el,v,q);};
  setStat('[data-bx-clock]','5:59am',true);setStat('[data-bx-auto]','0',true);setStat('[data-bx-you]','0',true);
  const playT=$('.t-morph',playBtn);
  function stale(){
    if(!played)return;run++;dirty=true;rowsEl.innerHTML='';showDone(false);playBtn.hidden=false;setRunning(false);
    if(playT)morphText(playT,'Run it with your changes');
    setStat('[data-bx-clock]','5:59am',true);setStat('[data-bx-auto]','0',true);setStat('[data-bx-you]','0',true);
    if(thinkBox)thinkSwap(thinkBox,'a day at '+ICP().site[0].toLowerCase());
  }
  async function play(){
    const id=++run;played=true;dirty=false;
    const ev=events();rowsEl.innerHTML='';showDone(false);playBtn.hidden=true;setRunning(true);
    let auto=0,you=0;setStat('[data-bx-auto]','0',true);setStat('[data-bx-you]','0',true);
    const stage=$('[data-bx-mock="run"]',root);
    for(const e of ev){
      if(id!==run)return;
      if(e.k==='you')you++;else auto++;
      rowsEl.insertAdjacentHTML('beforeend',rowHTML(e));
      const li=rowsEl.lastElementChild;
      setStat('[data-bx-clock]',clock(e.m),RM);setStat('[data-bx-auto]',String(auto),RM);setStat('[data-bx-you]',String(you),RM);
      if(thinkBox)thinkSwap(thinkBox,e.k==='you'?'waiting on you':e.t.toLowerCase());
      void li.offsetHeight;li.classList.add('is-shown');
      if(!RM){
        rowsEl.scrollTop=rowsEl.scrollHeight;
        if(e.site&&stage){
          const toast=$('[data-bm-toast]',stage),w=e.w&&stage.querySelector('[data-w="'+e.w.replace(/"/g,'\\"')+'"]');
          if(toast){toast.textContent=TOAST[e.site]||TOAST.form;toast.classList.remove('is-open');void toast.offsetWidth;toast.classList.add('is-open');
            clearTimeout(toast._t);toast._t=setTimeout(()=>toast.classList.remove('is-open'),1800);}
          $$('.bm-w.hit',stage).forEach(x=>x.classList.remove('hit'));if(w)w.classList.add('hit');
          if(w&&e.site==='calc'){const a=$('.bm-amt',w);if(a)a.textContent=['$860','$1,240','$2,150','$3,400'][Math.random()*4|0];}
        }
        await sleep(e.k==='you'?900:620);
      }
    }
    if(id!==run)return;
    const mins=you*2;
    $('[data-bx-sum]',root).textContent='One day. '+plural(auto,'thing')+' done on its own. '+(you?'You stepped in '+(you===1?'once':you+' times')+', about '+mins+' minutes.':"You didn't have to do a thing.");
    showDone(true);setRunning(false);
    if(thinkBox)thinkSwap(thinkBox,'day done / '+plural(auto+you,'thing'));
    const t=$('[data-bm-toast]',root);if(t)t.classList.remove('is-open');
  }
  playBtn.addEventListener('click',play);
  $('[data-bx-again]',root).addEventListener('click',play);
  const runEl=$('.bx-run',root);
  if(hasIO&&runEl){
    new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting&&(!played||dirty))play();}),{threshold:.35}).observe(runEl);
  }
  // the build bar shows up once you're into the steps
  const bar=$('[data-bx-bar]',root);
  if(bar){
    root.classList.add('bx-js');let tick=false;
    const place=()=>{tick=false;const r=root.getBoundingClientRect();bar.classList.toggle('on',r.top<innerHeight*.4&&r.bottom>innerHeight*.6);};
    addEventListener('scroll',()=>{if(!tick){tick=true;requestAnimationFrame(place);}},{passive:true});addEventListener('resize',place);place();
  }
  renderTools();sync();
})();

/* ---------- loader (once per visit) ---------- */
(function(){
  const html=document.documentElement,L=$('#loader');
  const hx=$('#h1.h1-x');if(hx&&!RM)hx.classList.add('x-pre');
  const heroWrap=$('.hero .wrap'),heroLines=heroWrap?$$('.hero .wrap>.lede,.hero .wrap>.spots,.hero .wrap>.actions,.hero .wrap>.htabs',heroWrap):[];
  if(!RM&&heroLines.length){heroWrap.classList.add('t-stagger');heroLines.forEach((el,i)=>el.classList.add('t-stagger-line','t-stagger-line--'+Math.min(4,i+1)));}
  const after=()=>{decode($('#h1'));if(hx&&!RM)setTimeout(()=>hx.classList.add('x-on'),1250);
    if(heroLines.length&&!RM)setTimeout(()=>heroWrap.classList.add('is-shown'),380);};
  if(!html.classList.contains('is-loading')||!L){if(L)L.remove();after();return;}
  const n=$('#ld-n'),fill=$('#ld-fill'),log=$('#ld-log');
  const lines=[['> oplev'],['who','an agency'],['what','the ultimate business engine'],['engines','water / earth / fire / wind'],['built for','your company'],['> hello']];
  const fmt=l=>l.length===1?esc(l[0]):'  '+l[0]+' '+'.'.repeat(Math.max(3,19-l[0].length))+' <b>'+l[1]+'</b>';
  const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
  const fontsP=Promise.race([document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve(),sleep(2600)]);
  const t0=performance.now();let done=false,shown=0;
  function exit(){
    if(done)return;done=true;
    try{sessionStorage.setItem('oplev-boot','1')}catch(e){}
    L.classList.add('out');html.classList.remove('is-loading');
    requestAnimationFrame(()=>requestAnimationFrame(()=>L.classList.add('gone')));
    setTimeout(()=>{L.remove();},950);
    after();
  }
  setTimeout(exit,5000);
  function frame(now){
    if(done)return;
    const t=Math.min(1,(now-t0)/1550),e=ease(t);
    n.textContent=String(Math.round(e*100)).padStart(3,'0');
    fill.style.transform='scaleX('+e.toFixed(4)+')';
    const want=Math.max(1,Math.ceil(e*lines.length));
    if(want!==shown){shown=want;log.innerHTML=lines.slice(0,want).map(fmt).join('\n');}
    if(t<1)requestAnimationFrame(frame);else fontsP.then(()=>sleep(240)).then(exit);
  }
  requestAnimationFrame(frame);
})();
})();
