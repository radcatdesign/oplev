(function(){
'use strict';
let RM=false;try{RM=matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}
const $=(s,r)=>(r||document).querySelector(s);
const $$=(s,r)=>Array.from((r||document).querySelectorAll(s));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pad2=n=>String(n).padStart(2,'0');
const WHO={'@ops':'Ops','@agents':'Agents','@leads':'Leads','you':'You'};
const hasIO='IntersectionObserver' in window;
function once(els,fn,threshold){
  els=els.filter(Boolean);if(!els.length)return;
  if(!hasIO){els.forEach(fn);return;}
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){io.unobserve(e.target);fn(e.target);}}),{threshold:threshold||.35});
  els.forEach(el=>io.observe(el));
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
    el.setAttribute('aria-label',r.finals.join('').replace(/\s+/g,' ').trim());
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
$$('.step,.svc').forEach(s=>s.addEventListener('mouseenter',()=>{decode($('.h3',s),360);pixDecode($('.px',s),420);}));
if(!RM)once([$('.steps'),$('.offer')],el=>$$('.px',el).forEach((svg,i)=>setTimeout(()=>pixDecode(svg,900),i*140)));

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
    d.innerHTML='<span class="ts">'+esc(r[0])+'</span><span class="ac'+(r[4]?' '+esc(r[4]):'')+(eng?' e-'+r[1].slice(1):'')+(!eng&&!WHO[r[1]]?' ext':'')+'">'+esc(who)+'</span><span class="msg">'+esc(r[2])+'</span><span class="res">'+esc(r[3])+'</span>';
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
      +'<div class="actions"><a class="btn" id="js-start">Start a project</a><a class="btn ghost" id="js-demo">Try the demo</a></div></div>';
    document.body.appendChild(dlg);
    $('.sheet-x',dlg).addEventListener('click',close);
    dlg.addEventListener('click',e=>{if(e.target===dlg)close();});
    dlg.addEventListener('close',()=>{if(ctl)ctl.stop();document.documentElement.classList.remove('sheet-open');if(opener&&opener.focus)opener.focus();});
    $('.replay',dlg).addEventListener('click',()=>ctl&&ctl.run());
  }
  function close(){if(dlg&&dlg.open)dlg.close();}
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
    st.href=J.start;st.innerHTML='Start a project <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M2.5 7h9M8 3.5 11.5 7 8 10.5"/></svg>';
    dm.href=J.demo;dm.innerHTML='Try the demo <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M2.5 7h9M8 3.5 11.5 7 8 10.5"/></svg>';
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
$$('.eng').forEach(e=>e.addEventListener('mouseenter',()=>{decode($('.eng-name',e),420,CAPS+'abcdefghijklmnopqrstuvwxyz');pixDecode($('.px',e),420);}));
if(!RM)once([$('.engines')],el=>$$('.px',el).forEach((svg,i)=>setTimeout(()=>pixDecode(svg,900),i*160)));

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
      if(good)el.removeAttribute('aria-invalid');else{el.setAttribute('aria-invalid','true');if(!first)first=el;}
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
    const rows=[['Name',d.name],['Email',d.email],['Company',d.company],['Business',d.type],['Team size',d.team],
      ['Build',(d.build||[]).join(', ')],['License',d.license],['Sell to others',d.resale],['Start',d.timing]];
    return rows.filter(r=>r[1]).map(r=>r[0]+': '+r[1]).join('\n')+'\n\nWhat still runs through me:\n'+(d.message||'');
  }
  function fallback(d){
    const text=compose(d);
    out(['<span class="chip">[!]</span> this form can\'t send from here yet.','  email it to <b>'+esc(MAIL)+'</b> and we\'ll take it from there. your note is ready to copy:']);
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
    out(['> sending inquiry ...']);
    let ok=false,code=0,msg='';
    try{
      const r=await fetch(f.getAttribute('action'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
      code=r.status;const j=await r.json().catch(()=>({}));ok=r.ok&&j.ok===true;msg=j.error||'';
    }catch(err){}
    btn.disabled=false;
    if(ok){
      out(['> sending inquiry ... <b>ok</b>','  received ............ <b>ok</b>','  routed to ........... <b>oplev team</b>','<span class="chip">[ok]</span> thanks, '+first+'. we\'ll be in touch soon.']);
      f.reset();try{localStorage.removeItem(KEY);}catch(err){}
    }else if(code===400&&msg){
      out(['<span class="chip">[!]</span> '+esc(msg)]);
    }else{
      fallback(d);
    }
  });
});

/* ---------- hover + scroll decodes ---------- */
$$('.links a,.btn').forEach(el=>onHover(el,()=>decode(el,360)));
onHover($('.nav .brand'),()=>decode($('.brand-t'),360,CAPS));
$$('.plan').forEach(p=>p.addEventListener('mouseenter',()=>decode($('.h3',p),360)));
$$('.ev').forEach(p=>p.addEventListener('mouseenter',()=>decode($('.h3',p),360)));
if(!RM){
  once($$('.h2'),el=>decode(el));
  once([$('.plans')],el=>$$('.amt',el).forEach((a,i)=>setTimeout(()=>decode(a,700),i*160)),.3);
  once([$('#wm')],()=>decode($('#wm-t'),null,CAPS));
}

/* ---------- footer wordmark fit + redraw on resize ---------- */
function fitWordmark(){
  const wm=$('#wm'),t=$('#wm-t');if(!wm||!t)return;
  wm.style.fontSize='';
  const avail=wm.clientWidth,w=t.getBoundingClientRect().width;
  if(w>avail&&avail>0){const fs=parseFloat(getComputedStyle(wm).fontSize);wm.style.fontSize=(fs*avail/w*.98)+'px';}
}
let rz;addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>{fitWordmark();drawAllMinis();refreshThumbs(false);},150);});
fitWordmark();
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{fitWordmark();refreshThumbs(true);});

/* ---------- loader (once per visit) ---------- */
(function(){
  const html=document.documentElement,L=$('#loader');
  const after=()=>{decode($('#h1'));fitWordmark();};
  if(!html.classList.contains('is-loading')||!L){if(L)L.remove();after();return;}
  const n=$('#ld-n'),fill=$('#ld-fill'),log=$('#ld-log');
  const lines=[['> oplev'],['who','an agency'],['what','custom engines'],['engines','ops / agents / leads'],['built for','your company'],['> hello']];
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
