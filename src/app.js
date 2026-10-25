(function(){
'use strict';
/* ================= data + helpers ================= */
const D=JSON.parse(document.getElementById('app-data').textContent);
const ENG=D.engines, ENGN=Object.fromEntries(ENG.map(e=>[e.id,e]));
const SETS=D.setups, SET=Object.fromEntries(SETS.map(s=>[s.id,s]));
const LIC=D.licenses, TIER=['one','core','company'];
const FUNCS=['Planning','Getting customers','Doing the work','Team','Day-to-day','Money','Customer care','Approvals and rules'];
const DIMS=[0,1,2,3,4];
const LEVELS=['Not set up','Runs on one person','Partly handled','Runs without you'];
const FUNC_E={'Planning':'ops','Getting customers':'leads','Doing the work':'ops','Team':'ops','Day-to-day':'ops','Money':'agents','Customer care':'agents','Approvals and rules':'ops'};
const FUNC_TIP={'Planning':'Put your goals and weekly numbers on one screen.','Getting customers':'Save every lead and answer it within minutes.','Doing the work':'Make the work run the same way every time.','Team':'Set up every new person the same way.','Day-to-day':'Hand routine jobs to automations.','Money':'Send invoice reminders and match payments automatically.','Customer care':'Follow up with every client without anyone having to remember.','Approvals and rules':'Decide what needs a person, and log everything else.'};
const STAGES=['New','In conversation','Booked','Won','Lost'];
const TRIGGERS=['when a form or chat comes in','when a new inquiry comes in','on your website','every hour','every morning at 6','every Monday','every Friday','first of the month','after every visit','after a job is done','24 hours before a visit','3 days after a quote','7 days after an invoice is due','when a client misses a visit','when a client misses a booking','when stock runs low','when someone joins','when a contract is signed'];
let RM=false;try{RM=matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}
const $=(s,r)=>(r||document).querySelector(s), $$=(s,r)=>Array.from((r||document).querySelectorAll(s));
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pad2=n=>String(n).padStart(2,'0');
const clock=()=>{const d=new Date();return pad2(d.getHours())+':'+pad2(d.getMinutes())+':'+pad2(d.getSeconds());};
const money=v=>'$'+Math.round(Number(v)||0).toLocaleString('en-US');
const first=n=>String(n||'').trim().split(/\s+/)[0]||'there';
const initials=n=>String(n||'?').split(/\s+/).map(w=>w[0]).join('').slice(0,2).toUpperCase();
function hashStr(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;}
function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const tag=e=>ENGN[e]?`<span class="etag e-${e}">${esc(ENGN[e].name)}</span>`:'';
const WHO={'@ops':'Ops','@agents':'Agents','@leads':'Leads','you':'You'};
const actorCls=a=>/^@[a-z]+$/.test(a)?' e-'+a.slice(1):'';

/* ================= decode (headline scramble) ================= */
const UP='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+=/<>[]{}_', LO='abcdefghijklmnopqrstuvwxyz0123456789#%&*+=/<>_';
function decode(el,dur){
  if(RM||!el)return;
  const nodes=[],w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
  while(w.nextNode())if(w.currentNode.nodeValue.trim())nodes.push(w.currentNode);
  const fin=nodes.map(n=>n.nodeValue),total=fin.join('').length;if(!total)return;
  el.setAttribute('aria-label',fin.join('').replace(/\s+/g,' ').trim());
  dur=dur||Math.min(1100,320+total*18);let off=0;
  const at=fin.map(s=>{const a=[];for(let i=0;i<s.length;i++)a.push(((off+i)/total)*dur*.62+Math.random()*dur*.38);off+=s.length;return a;});
  const cur=fin.map(s=>s.split('')),t0=performance.now();let last=0;
  const pick=s=>s[Math.random()*s.length|0];
  (function f(now){
    if(!el.isConnected)return;
    const e=now-t0,swap=now-last>50;if(swap)last=now;let done=true;
    fin.forEach((s,k)=>{for(let i=0;i<s.length;i++){const c=s[i];if(/\s/.test(c)||e>=at[k][i])cur[k][i]=c;else{done=false;if(swap||cur[k][i]===c)cur[k][i]=c>='a'&&c<='z'?pick(LO):pick(UP);}}nodes[k].nodeValue=cur[k].join('');});
    if(!done)requestAnimationFrame(f);
  })(t0);
}

/* ================= state ================= */
const KEY='oplev-console-v1';
let S=null, route='overview', drawer=null;
const ui={apSel:null,actF:'all',actQ:'',playF:'all',pipeF:'all',recQ:'',setTab:'team',wz:null};

function init(type,o){
  o=o||{};
  const s=SET[type]||SETS[0], d=s.demo, r=rng(hashStr(type+(o.biz||'')));
  const licensed=(o.engines||s.engines).slice();
  const license=o.license||TIER[Math.max(0,licensed.length-1)];
  let seq=1;const id=()=>'i'+(seq++);
  const plays=[];
  s.uses.forEach(([e,trig,title,desc],i)=>{
    const on=licensed.includes(e)&&(!o.plays||o.plays.includes(title));
    plays.push({id:id(),e,trig,title,desc,added:on,on,appr:i%2===0,runs:on?8+Math.floor(r()*40):0,last:on?(2+Math.floor(r()*55))+' min ago':'never',setup:true});
  });
  D.plays.forEach(([e,trig,title,desc])=>{
    if(plays.some(p=>p.title===title))return;
    const on=!!(o.plays&&o.plays.includes(title)&&licensed.includes(e));
    plays.push({id:id(),e,trig,title,desc,added:on,on,appr:true,runs:0,last:'never'});
  });
  const approvals=d.approvals.filter(a=>licensed.includes(a.e)).map((a,i)=>Object.assign({},a,{id:id(),age:(4+i*17)+' min ago'}));
  const log=s.day.map(x=>({t:x[0],a:x[1],m:x[2],r:x[3],f:x[4]||''})).filter(x=>x.a==='you'||licensed.includes(x.a.slice(1)));
  const leads=d.leads.map(([n,src,stage,val,owner,last])=>({id:id(),n,src,stage,val,owner,last}));
  const records=d.records.map(([n,kind,status,owner,upd])=>({id:id(),n,kind,status,owner,upd}));
  const extra=['Slack','Zapier','QuickBooks','Google Drive','Calendly'].filter(x=>!s.connects.includes(x)).slice(0,3);
  const integrations=s.connects.map(n=>({n,on:o.conns?!!o.conns[n]:true})).concat(extra.map(n=>({n,on:false})));
  const counts={},running={};
  ENG.forEach(e=>{counts[e.id]=licensed.includes(e.id)?9+Math.floor(r()*36):0;running[e.id]=true;});
  const [prev,now]=d.score;
  const m=FUNCS.map(()=>DIMS.map(()=>Math.max(0,Math.min(3,Math.round(now/100*3+(r()-.5)*1.7)))));
  const trend=Array.from({length:8},(_,i)=>Math.round(prev+(now-prev)*(i/7)+(i&&i<7?(r()-.5)*4:0)));
  const people=(o.owner?[[o.owner,'Owner']].concat(d.people.slice(1)):d.people).map(([name,role])=>({name,role}));
  return {v:1,type:s.id,biz:o.biz||d.biz,people,license,licensed,running,plays,approvals,log,leads,records,kpis:d.kpis,integrations,
    rules:Object.assign({newClient:true,money:true,amt:500,contracts:true,bulk:true,refunds:true},o.rules||{}),
    counts,score:{prev,now,m,trend},live:true,seq,tick:0};
}
function nid(){return 'i'+(S.seq++);}
let saveT=0;
function save(){clearTimeout(saveT);saveT=setTimeout(()=>{try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}},150);}
function load(){try{const x=JSON.parse(localStorage.getItem(KEY)||'null');if(x&&x.v===1&&SET[x.type])return x;}catch(e){}return null;}
const owner=()=>(S.people[0]&&S.people[0].name)||'there';
const setup=()=>SET[S.type];
const has=e=>S.licensed.includes(e);
const isOn=e=>has(e)&&S.running[e];
function pushLog(a,m,r,f){
  const entry={t:clock(),a,m,r,f:f||''};S.log.push(entry);if(S.log.length>300)S.log.splice(0,S.log.length-300);
  if(/^@/.test(a)&&S.counts[a.slice(1)]!=null)S.counts[a.slice(1)]++;
  liveInsert(entry);return entry;
}

/* ================= shell ================= */
const NAV=[
  [null,[['overview','Home'],['approvals','Needs your OK','badge'],['activity','Activity']]],
  ['Engines',[['engine-ops','Ops','e'],['engine-agents','Agents','e'],['engine-leads','Leads','e'],['plays','Automations']]],
  ['Your business',[['pipeline','Inquiries'],['records','Records'],['score','Progress score']]],
  ['Account',[['setup','Set up'],['settings','Settings']]]
];
function shell(){
  const app=$('#app');
  app.innerHTML=`
  <aside class="side" id="side" aria-label="Console navigation">
    <div class="side-top"><a class="brand" href="index.html" aria-label="OpLev site"><svg class="mark" viewBox="0 0 10 10" aria-hidden="true"><path fill="#F2F2EF" d="M0 0h10v2H0zM0 8h10v2H0zM0 2h2v6H0zM8 2h2v6H8zM4 4h2v2H4z"/></svg><span>OPLEV</span></a><span class="label">console</span></div>
    <div class="ws" id="ws"></div>
    <nav class="side-nav" id="side-nav"></nav>
    <div class="side-foot" id="side-foot"></div>
  </aside>
  <div class="scrim" data-act="side-close"></div>
  <div class="mainc">
    <header class="tbar">
      <button class="menu-btn side-btn" type="button" data-act="side-open" aria-label="Open navigation"><span class="bars" aria-hidden="true"></span><span class="mb-t">Menu</span></button>
      <span class="crumb" id="crumb"></span>
      <div class="top-r">
        <button class="live-btn" type="button" data-act="live" id="live-btn"><span class="dot" aria-hidden="true"></span><span class="lb-t">live</span></button>
        <span class="clock label" id="clk"></span>
        <span class="avatar" id="avatar" title=""></span>
      </div>
    </header>
    <div class="demo-bar"><span><b>This is a demo.</b> Everything here is sample data, and your changes stay in this browser.</span><a href="start.html">Get this for your business &rarr;</a></div>
    <main class="view" id="view" tabindex="-1"></main>
  </div>
  <div id="drawer-root"></div>
  <div id="toast-root"></div>`;
}
function renderSide(){
  const s=setup(),L=LIC[S.license];
  $('#ws').innerHTML=`<button class="ws-btn" type="button" data-act="ws" aria-expanded="false" aria-controls="ws-menu"><span class="ws-mark">${esc(initials(S.biz))}</span><span class="ws-txt"><span class="ws-name">${esc(S.biz)}</span><span class="ws-type">${esc(s.name)}</span></span><span class="ws-caret">&#9662;</span></button>
  <div class="ws-menu" id="ws-menu" hidden><span class="label">sample workspaces</span>${SETS.map(x=>`<button class="ws-opt" type="button" data-act="ws-pick" data-id="${x.id}" aria-current="${x.id===S.type}"><span>${esc(x.demo.biz)}</span><span>${esc(x.type.split(' ')[0])}</span></button>`).join('')}<div class="ws-sep"></div><button class="ws-opt" type="button" data-act="reset"><span>Reset this demo</span><span></span></button><button class="ws-opt" type="button" data-act="go" data-r="setup"><span>Set up a new workspace</span><span></span></button></div>`;
  $('#side-nav').innerHTML=NAV.map(([g,items])=>`<div class="nav-g">${g?`<span class="label">${g}</span>`:''}${items.map(([r,t,x])=>{
    let cls='nav-i',right='';
    if(x==='e'){const e=r.slice(7);cls+=' e-'+e+(has(e)?'':' locked');right=has(e)?(S.running[e]?'':'<span class="ni-r">paused</span>'):'<span class="ni-r">not in plan</span>';return `<a class="${cls}" href="#${r}"${route===r?' aria-current="page"':''}><span class="ni-mk"></span>${t}${right}</a>`;}
    if(x==='badge')right=`<span class="badge" data-n="${S.approvals.length}" id="ap-badge">${S.approvals.length}</span>`;
    return `<a class="${cls}" href="#${r}"${route===r||(r==='engine-ops'&&false)?' aria-current="page"':''}>${t}${right}</a>`;
  }).join('')}</div>`).join('');
  $('#side-foot').innerHTML=`<div class="lic-mini"><span class="label">your plan</span><b>${esc(L.name)} / ${esc(L.price)}</b></div><div class="etags">${S.licensed.map(tag).join('')}</div><a class="label" href="pricing.html">Plans &rarr;</a><a class="label" href="index.html">&larr; Back to site</a>`;
  const lb=$('#live-btn');lb.setAttribute('aria-pressed',String(S.live));lb.title=S.live?'Pause live activity':'Resume live activity';
  $('#avatar').textContent=initials(owner());$('#avatar').title=owner();
}
const ROUTE_NAME={overview:'Home',approvals:'Needs your OK',activity:'Activity',engines:'Engines','engine-ops':'Ops','engine-agents':'Agents','engine-leads':'Leads',plays:'Automations',pipeline:'Inquiries',records:'Records',score:'Progress score',setup:'Set up',settings:'Settings'};
function setCrumb(){$('#crumb').innerHTML=`${esc(S.biz)} / <b>${esc(ROUTE_NAME[route]||'Home')}</b>`;}

/* ================= views ================= */
function greet(){const h=new Date().getHours();return h<12?'Good morning':h<18?'Good afternoon':'Good evening';}
function bars(seed,n){const r=rng(hashStr(seed));return Array.from({length:n||14},()=>`<i style="height:${12+Math.round(r()*88)}%"></i>`).join('');}
function rowHTML(x){return `<div class="row"><span class="ts">${esc(x.t)}</span><span class="ac${x.f?' '+x.f:''}${actorCls(x.a)}">${esc(WHO[x.a]||x.a)}</span><span class="msg">${esc(x.m)}</span><span class="res">${esc(x.r)}</span></div>`;}
function feedRows(list,max){const rows=list.slice(-max).reverse();return rows.length?rows.map(rowHTML).join(''):'<div class="feed-empty">Nothing yet.</div>';}
function head(path,title,sub,actions,cls){return `<div class="v-head"><div class="v-head-l"><h1 class="v-title${cls?' '+cls:''}">${title}</h1>${sub?`<p class="v-sub">${sub}</p>`:''}</div>${actions?`<div class="v-actions">${actions}</div>`:''}</div>`;}
const playsOn=e=>S.plays.filter(p=>p.e===e&&p.added&&p.on).length;

function vOverview(){
  const n=S.approvals.length;
  const sub=n?`${n} thing${n===1?' needs':'s need'} your OK. Everything else is handled.`:'Nothing needs you. Everything else is handled.';
  const needs=S.approvals.slice(0,4).map(a=>`<li><a href="#approvals" data-act="ap-go" data-id="${a.id}">${tag(a.e)}<span class="nl-t">${esc(a.kind)}: ${esc(a.to)}</span></a></li>`).join('');
  const tiles=ENG.map(e=>{
    const L=!has(e.id),st=L?'<span class="state lock">not in your plan</span>':(S.running[e.id]?'<span class="state on">running</span>':'<span class="state">paused</span>');
    return `<a class="cell etile e-${e.id}${L?' locked':''}" href="#engine-${e.id}"><div class="et-top"><span class="label">${esc(e.triad)}</span>${st}</div><div class="et-name">${esc(e.name)}</div>
    <div class="et-stats"><div><b data-k="count-${e.id}">${S.counts[e.id]}</b><span class="label">done today</span></div><div><b>${playsOn(e.id)}</b><span class="label">automations on</span></div></div><div class="bars" aria-hidden="true">${bars(S.type+e.id)}</div></a>`;}).join('');
  const kp=S.kpis.map(([l,v,s])=>`<div class="cell kpi"><span class="label">${esc(l)}</span><b>${esc(v)}</b><span class="label">${esc(s)}</span></div>`).join('');
  const sc=S.score,d=sc.now-sc.prev;
  return head('overview',`${greet()}, ${esc(first(owner()))}.`,sub,n?`<a class="btn" href="#approvals">Review approvals</a>`:`<a class="btn ghost" href="#activity">See activity</a>`)+`
  <div class="g ov-top">
    <div class="cell"><div class="et-top"><span class="label">needs your OK</span><a class="lnk" href="#approvals">open &rarr;</a></div><div class="big-n" data-k="ap-count">${n}</div>${n?`<ul class="needs-l">${needs}</ul>`:'<p class="v-sub">Inbox zero.</p>'}</div>
    ${tiles}
  </div>
  <div class="g g4">${kp}</div>
  <div class="ov-bottom">
    <section class="pnl"><div class="pnl-hd"><span class="label">happening now</span><a class="label" href="#activity">all activity &rarr;</a></div><div class="feed" data-live data-max="14">${feedRows(S.log,14)}</div></section>
    <section class="pnl score-card"><div class="et-top"><span class="label">progress score</span><a class="lnk" href="#score">details &rarr;</a></div><div class="big-n">${sc.now}</div><span class="label">${d>=0?'+':''}${d} since you started</span><div class="trend" aria-hidden="true">${sc.trend.map(v=>`<i style="height:${Math.max(8,v)}%"></i>`).join('')}</div><p class="v-sub" style="font-size:14px">${esc(levelOf(sc.now))}. ${esc(FUNC_TIP[weakest()[0].f])}</p></section>
  </div>`;
}

function vApprovals(){
  const list=S.approvals;
  if(!list.length)return head('approvals','Needs your OK','Nothing important goes out until you say yes.')+`<div class="pnl empty"><div class="big-n">0</div><p>Nothing needs you right now. When an engine wants to send, spend or promise something, it lands here first.</p><a class="btn ghost" href="#activity">See what ran</a></div>`;
  if(!list.some(a=>a.id===ui.apSel))ui.apSel=list[0].id;
  return head('approvals','Needs your OK','Nothing important goes out until you say yes. You can edit anything first.')+`
  <div class="ap-wrap"><div class="ap-list" id="ap-list">${apList()}</div><div class="ap-detail" id="ap-detail">${apDetail()}</div></div>`;
}
function apList(){return S.approvals.map(a=>`<button class="ap-item" type="button" data-act="ap-sel" data-id="${a.id}" aria-current="${a.id===ui.apSel}">${tag(a.e)}<span class="api-t">${esc(a.kind)}</span><span class="label">${esc(a.age)}</span><span class="api-s">${esc(a.to)}</span></button>`).join('');}
function apDetail(){
  const a=S.approvals.find(x=>x.id===ui.apSel);if(!a)return '';
  return `<div class="et-top">${tag(a.e)}<span class="label">${esc(a.age)}</span></div>
  <h2 class="ap-d-t">${esc(a.kind)}</h2><dl class="kv"><dt>to</dt><dd>${esc(a.to)}</dd><dt>engine</dt><dd>${esc(ENGN[a.e].name)}</dd></dl>
  <div class="why"><span class="label">why it's here</span><span>${esc(a.why)}</span></div>
  <label class="fl"><span class="label">draft</span><textarea class="inp ap-draft" id="ap-draft" rows="7">${esc(a.draft)}</textarea></label>
  <div class="ap-btns"><button class="btn" type="button" data-act="ap-ok" data-id="${a.id}">Approve and send</button><button class="btn ghost" type="button" data-act="ap-no" data-id="${a.id}">Don't send</button><span class="label" style="margin-left:auto">nothing goes out until you approve</span></div>`;
}

function filteredLog(){
  const q=ui.actQ.trim().toLowerCase();
  return S.log.filter(x=>(ui.actF==='all'||(ui.actF==='you'?x.a==='you':x.a==='@'+ui.actF))&&(!q||(x.m+' '+x.r+' '+x.a).toLowerCase().includes(q)));
}
function vActivity(){
  const f=[['all','All'],['ops','Ops'],['agents','Agents'],['leads','Leads'],['you','You']];
  return head('activity','Activity','Everything your engines did, as it happens.')+`
  <div class="toolbar"><div class="tabs filters" role="group" aria-label="Filter by engine">${f.map(([k,t])=>`<button class="tab${ENGN[k]?' e-'+k:''}" type="button" data-act="act-f" data-f="${k}" aria-pressed="${ui.actF===k}">${t}</button>`).join('')}</div>
  <label class="search"><span class="sr">Search activity</span><input class="inp" id="act-q" type="search" placeholder="Search activity" value="${esc(ui.actQ)}" autocomplete="off"></label></div>
  <section class="pnl"><div class="pnl-hd"><span class="label" id="act-count">${filteredLog().length} events</span><span class="label">${S.live?'live':'paused'}</span></div><div class="feed" data-live data-filter data-max="200" style="max-height:none">${feedRows(filteredLog(),200)}</div></section>`;
}

function vEngines(){
  return head('engines','Engines','Your plan decides which ones run.')+`<div class="g g3">${ENG.map(e=>{
    const L=!has(e.id);
    return `<a class="cell etile e-${e.id}${L?' locked':''}" href="#engine-${e.id}"><div class="et-top"><span class="label">${esc(e.triad)}</span>${L?'<span class="state lock">not in your plan</span>':(S.running[e.id]?'<span class="state on">running</span>':'<span class="state">paused</span>')}</div><div class="et-name">${esc(e.name)}</div><p class="v-sub" style="font-size:15px">${esc(e.line)}</p>
    <div class="et-stats"><div><b data-k="count-${e.id}">${S.counts[e.id]}</b><span class="label">done today</span></div><div><b>${playsOn(e.id)}</b><span class="label">automations on</span></div></div><span class="lnk">${L?'Add to your plan':'Open'} &rarr;</span></a>`;}).join('')}</div>`;
}
function triggerSel(p){const opts=TRIGGERS.includes(p.trig)?TRIGGERS:[p.trig].concat(TRIGGERS);return `<select class="dd" data-act="play-trig" data-id="${p.id}" aria-label="When ${esc(p.title)} runs">${opts.map(t=>`<option${t===p.trig?' selected':''}>${esc(t)}</option>`).join('')}</select>`;}
function vEngine(eid){
  const e=ENGN[eid];
  if(!has(eid)){
    const next=TIER[Math.min(2,S.licensed.length)],L=LIC[next];
    const preview=S.plays.filter(p=>p.e===eid).slice(0,5);
    return head('engines/'+eid,esc(e.name),esc(e.triad)+' '+esc(e.line),'',`ec e-${eid}`)+`
    <div class="lock-card e-${eid}"><div style="display:flex;flex-direction:column;gap:16px"><span class="label">not in your plan yet</span><h2>Add ${esc(e.name)} and move to ${esc(L.name)}, ${esc(L.price)} a month.</h2><p>${esc(e.line)} It works with the engines you already have, so nothing gets set up twice.</p><div class="v-actions"><button class="btn" type="button" data-act="lic-add" data-e="${eid}">Add ${esc(e.name)} to this demo</button><a class="btn ghost" href="start.html#${next}">Talk to us</a></div></div>
    <div><ul class="rowlist">${e.caps.map(c=>`<li>${esc(c)}</li>`).join('')}</ul><p class="label" style="margin:18px 0 10px">automations you'd get</p><div class="etags">${preview.map(p=>`<span class="etag e-${eid}">${esc(p.title)}</span>`).join('')}</div></div></div>`;
  }
  const mine=S.plays.filter(p=>p.e===eid&&p.added);
  const waiting=S.approvals.filter(a=>a.e===eid).length;
  const lastE=[...S.log].reverse().find(x=>x.a==='@'+eid);
  const rows=mine.map(p=>`<tr class="${p.on&&S.running[eid]?'':'off'}"><td><button class="sw e-${eid}" type="button" role="switch" aria-checked="${p.on}" data-act="play-on" data-id="${p.id}" aria-label="Turn ${esc(p.title)} ${p.on?'off':'on'}"></button></td>
    <td><div class="pt-title"><b>${esc(p.title)}</b><span>${esc(p.desc)}</span></div></td><td>${triggerSel(p)}</td>
    <td><label class="ck-l"><input type="checkbox" data-act="play-appr" data-id="${p.id}"${p.appr?' checked':''}>check with me</label></td>
    <td class="num">${p.runs}</td><td class="num">${esc(p.last)}</td><td><button class="btn ghost btn-xs" type="button" data-act="play-run" data-id="${p.id}"${p.on&&S.running[eid]?'':' disabled'}>Run now</button></td></tr>`).join('');
  return head('engines/'+eid,esc(e.name),esc(e.triad)+' '+esc(e.line),`<button class="btn ghost" type="button" data-act="go-plays" data-e="${eid}">Add automations</button>`,`ec e-${eid}`)+`
  <div class="e-${eid}"><div class="eh-row"><span class="state${S.running[eid]?' on':''}">${S.running[eid]?'running':'paused'}</span><span class="label">${S.running[eid]?'pause everything in this engine':'turn this engine back on'}</span><button class="sw" type="button" role="switch" aria-checked="${S.running[eid]}" data-act="eng-run" data-e="${eid}" aria-label="${S.running[eid]?'Pause':'Resume'} ${esc(e.name)}"></button></div>
  <div class="g g4" style="border-top:0"><div class="cell kpi"><span class="label">done today</span><b data-k="count-${eid}">${S.counts[eid]}</b></div><div class="cell kpi"><span class="label">automations on</span><b>${playsOn(eid)}</b></div><div class="cell kpi"><span class="label">waiting on you</span><b>${waiting}</b></div><div class="cell kpi"><span class="label">last action</span><b style="font-size:20px">${lastE?esc(lastE.t.slice(0,5)):'none'}</b></div></div></div>
  <div class="sec-t"><h2>Automations</h2><span class="label">${mine.length} in this engine</span></div>
  ${mine.length?`<div class="tbl-w"><table class="tbl"><thead><tr><th>On</th><th>Automation</th><th>When it runs</th><th>Your OK</th><th>Times run</th><th>Last run</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`:`<div class="pnl empty"><p>No automations in ${esc(e.name)} yet.</p><button class="btn ghost" type="button" data-act="go-plays" data-e="${eid}">Browse automations</button></div>`}
  <div class="sec-t"><h2>Recent activity</h2><a class="label" href="#activity" data-act="act-pre" data-f="${eid}">all &rarr;</a></div>
  <section class="pnl"><div class="feed" data-live data-engine="${eid}" data-max="10">${feedRows(S.log.filter(x=>x.a==='@'+eid),10)}</div></section>`;
}

function vPlays(){
  const f=[['all','All'],['ops','Ops'],['agents','Agents'],['leads','Leads']];
  const list=S.plays.filter(p=>ui.playF==='all'||p.e===ui.playF);
  return head('plays','Automations','Jobs your engines can take off your plate. Add any of them to an engine in your plan.')+`
  <div class="toolbar"><div class="tabs filters" role="group" aria-label="Filter automations">${f.map(([k,t])=>`<button class="tab${ENGN[k]?' e-'+k:''}" type="button" data-act="play-f" data-f="${k}" aria-pressed="${ui.playF===k}">${t}</button>`).join('')}</div></div>
  <ul class="plib">${list.map(p=>{
    let ft;
    if(!has(p.e))ft=`<span class="label">needs the ${esc(ENGN[p.e].name)} engine</span><a class="lnk" href="#engine-${p.e}">add it &rarr;</a>`;
    else if(p.added)ft=`<span class="label added e-${p.e}">in ${esc(ENGN[p.e].name)}${p.on?'':' / off'}</span><a class="lnk" href="#engine-${p.e}">open &rarr;</a>`;
    else ft=`<span class="label">available</span><button class="btn btn-xs" type="button" data-act="play-add" data-id="${p.id}">Add</button>`;
    return `<li class="e-${p.e}"><div class="pl-top">${tag(p.e)}<span class="label">runs ${esc(p.trig)}</span></div><h3>${esc(p.title)}</h3><p>${esc(p.desc)}</p><div class="pl-ft">${ft}</div></li>`;}).join('')}</ul>`;
}

function vPipeline(){
  const by=st=>S.leads.filter(l=>l.stage===st);
  const list=S.leads.filter(l=>ui.pipeF==='all'||l.stage===ui.pipeF);
  return head('pipeline','Inquiries','Everyone who has asked about working with you, in one list.',`<button class="btn ghost" type="button" data-act="pipe-f" data-f="all">Show all</button>`)+`
  <div class="g stages">${STAGES.map(st=>`<button class="stage" type="button" data-act="pipe-f" data-f="${st}" aria-pressed="${ui.pipeF===st}"><span class="label">${st}</span><b>${by(st).length}</b><span class="label">${money(by(st).reduce((a,l)=>a+l.val,0))}</span></button>`).join('')}</div>
  <div class="tbl-w"><table class="tbl"><thead><tr><th>Name</th><th>Source</th><th>Stage</th><th>Value</th><th>Owner</th><th>Last touch</th></tr></thead><tbody>${list.map(l=>`<tr class="click" data-act="lead-open" data-id="${l.id}" tabindex="0"><td class="n">${esc(l.n)}</td><td>${esc(l.src)}</td><td><span class="st-chip s-${l.stage.split(' ')[0]}">${esc(l.stage)}</span></td><td class="num">${money(l.val)}</td><td>${esc(l.owner)}</td><td class="num">${esc(l.last)}</td></tr>`).join('')||'<tr><td colspan="6">No leads in this stage.</td></tr>'}</tbody></table></div>`;
}

function vRecords(){
  const q=ui.recQ.trim().toLowerCase();
  const list=S.records.filter(r=>!q||(r.n+' '+r.kind+' '+r.status+' '+r.owner).toLowerCase().includes(q));
  return head('records','Records','Every client, order and job in one place. Your engines keep them up to date.')+`
  <div class="toolbar"><label class="search" style="flex:1 1 260px"><span class="sr">Search records</span><input class="inp" id="rec-q" type="search" placeholder="Search records" value="${esc(ui.recQ)}" autocomplete="off"></label><span class="label">${S.records.length} records</span></div>
  <div class="tbl-w"><table class="tbl"><thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Owner</th><th>Updated</th></tr></thead><tbody id="rec-body">${recRows(list)}</tbody></table></div>`;
}
function recRows(list){return list.map(r=>`<tr class="click" data-act="rec-open" data-id="${r.id}" tabindex="0"><td class="n">${esc(r.n)}</td><td>${esc(r.kind)}</td><td>${esc(r.status)}</td><td>${esc(r.owner)}</td><td class="num">${esc(r.upd)}</td></tr>`).join('')||'<tr><td colspan="5">No matching records.</td></tr>';}

function levelOf(v){return v<25?LEVELS[0]:v<50?LEVELS[1]:v<75?LEVELS[2]:LEVELS[3];}
function weakest(){return FUNCS.map((f,i)=>({f,v:S.score.m[i].reduce((a,b)=>a+b,0)})).sort((a,b)=>a.v-b.v);}
function vScore(){
  const sc=S.score,d=sc.now-sc.prev,li=LEVELS.indexOf(levelOf(sc.now));
  const areas=FUNCS.map((f,i)=>{const v=S.score.m[i].reduce((x,y)=>x+y,0),pct=Math.round(v/15*100);return {f,pct,lv:levelOf(pct)};});
  const rows=areas.map(x=>`<li class="e-${FUNC_E[x.f]}"><span class="ar-n">${esc(x.f)}</span><span class="ar-bar" aria-hidden="true"><i style="width:${Math.max(4,x.pct)}%"></i></span><span class="ar-l">${esc(x.lv)}</span></li>`).join('');
  const nx=weakest().slice(0,3).map(w=>{const e=FUNC_E[w.f];return `<li class="e-${e}">${tag(e)}<div><b>${w.f}</b><p>${esc(FUNC_TIP[w.f])}</p></div><a class="lnk" href="#engine-${e}">${has(e)?'open':'add'} &rarr;</a></li>`;}).join('');
  return head('score','Progress score','How much of your business runs without you having to step in.')+`
  <div class="score-top"><div><span class="label">out of 100</span><div class="score-big">${sc.now}</div><span class="label">${d>=0?'+':''}${d} since you started / ${esc(levelOf(sc.now))}</span>
    <div class="lvlbar">${LEVELS.map((_,i)=>`<span class="${i<=li?'on':''}"></span>`).join('')}</div><div class="lvlbar-l">${LEVELS.map(l=>`<span>${l}</span>`).join('')}</div>
    <div class="trend" aria-hidden="true">${sc.trend.map(v=>`<i style="height:${Math.max(8,v)}%"></i>`).join('')}</div><span class="label">last 8 weeks</span></div>
  <div><div class="et-top"><span class="label">area by area</span></div><ul class="areas">${rows}</ul></div></div>
  <div class="sec-t"><h2>What to fix next</h2><span class="label">your three weakest areas</span></div>
  <section class="pnl"><ul class="next-l">${nx}</ul></section>
  <p class="note">This is a sample score. Your real score comes from a few short questions for you and your team.</p>`;
}

/* ---------- setup wizard ---------- */
const WZ=['Business','Plan','Connect','Automations','Approvals','Start'];
function wzInit(){const s=setup();ui.wz={step:0,name:'',owner:'',type:S.type,lic:s.license,engines:s.engines.slice(),conns:{},plays:null,rules:Object.assign({},S.rules),booted:false};}
function wzSetup(){return SET[ui.wz.type];}
function wzPlays(){const w=ui.wz,s=wzSetup();const list=s.uses.filter(u=>w.engines.includes(u[0])).map(u=>({e:u[0],trig:u[1],title:u[2],rec:true}));D.plays.forEach(p=>{if(w.engines.includes(p[0])&&!list.some(x=>x.title===p[2]))list.push({e:p[0],trig:p[1],title:p[2],rec:false});});return list;}
function vSetup(){
  if(!ui.wz)wzInit();
  const w=ui.wz,s=wzSetup(),need=TIER.indexOf(w.lic)+1;
  const steps=`<div class="wz-steps">${WZ.map((t,i)=>`<span class="${i<w.step?'done':i===w.step?'cur':''}"><b>${pad2(i+1)}</b>${t}</span>`).join('')}</div>`;
  let body='';
  if(w.step===0)body=`<h2>Tell us about the business.</h2><p class="v-sub">We use this to fill in sample data. Nothing leaves this browser.</p>
    <div class="inq-grid"><label class="fl"><span class="label">Business name *</span><input class="inp" id="wz-name" value="${esc(w.name)}" placeholder="Juniper Physio" autocomplete="organization"></label><label class="fl"><span class="label">Your name</span><input class="inp" id="wz-owner" value="${esc(w.owner)}" placeholder="Dana Ruiz" autocomplete="name"></label></div>
    <fieldset class="fs"><legend class="label">What kind of business?</legend><div class="choice c3">${SETS.map(x=>`<label><input type="radio" name="wz-type" value="${x.id}" data-act="wz-type"${x.id===w.type?' checked':''}><span class="label">${esc(x.type)}</span><b>${esc(x.name)}</b><p>${esc(x.pitch)}</p><span class="etags">${x.engines.map(tag).join('')}</span></label>`).join('')}</div></fieldset>`;
  if(w.step===1)body=`<h2>Pick a plan and your engines.</h2><p class="v-sub">The ${esc(s.name)} usually runs on ${s.engines.map(e=>ENGN[e].name).join(' + ')}.</p>
    <div class="choice c3">${TIER.map((t,i)=>`<label><input type="radio" name="wz-lic" value="${t}" data-act="wz-lic"${t===w.lic?' checked':''}><span class="label">plan ${i+1} of 3</span><b>${esc(LIC[t].name)}</b><p>${esc(LIC[t].price)} a month / ${i+1} of 3 engines</p></label>`).join('')}</div>
    <fieldset class="fs"><legend class="label">Choose ${need} engine${need>1?'s':''} (${w.engines.length} picked)</legend><div class="choice c3">${ENG.map(e=>`<label class="e-${e.id}"><input type="checkbox" value="${e.id}" data-act="wz-eng"${w.engines.includes(e.id)?' checked':''}>${tag(e.id)}<b>${esc(e.name)}</b><p>${esc(e.line)}</p></label>`).join('')}</div></fieldset>`;
  if(w.step===2){const all=s.connects.concat(['Slack','Zapier','QuickBooks'].filter(x=>!s.connects.includes(x)));
    body=`<h2>Connect your tools.</h2><p class="v-sub">Your engines work inside the apps you already use. In this demo, connecting just flips the switch.</p>
    <div class="conn">${all.map(n=>{const on=!!w.conns[n];return `<div class="${on?'on':''}"><span class="cn-ic">${esc(n[0])}</span><span class="cn-n">${esc(n)}</span><span class="cn-s">${on?'connected':''}</span><button class="btn ${on?'ghost ':''}btn-xs" type="button" data-act="wz-conn" data-n="${esc(n)}">${on?'Disconnect':'Connect'}</button></div>`;}).join('')}</div>`;}
  if(w.step===3){const list=wzPlays();if(!w.plays)w.plays=list.filter(p=>p.rec).map(p=>p.title);
    body=`<h2>Choose your automations.</h2><p class="v-sub">We picked the usual ones for the ${esc(s.name)}. Add or drop any of them.</p>
    <div class="rules">${list.map(p=>`<label class="rule e-${p.e}"><span>${tag(p.e)}</span><span class="r-t"><b>${esc(p.title)}</b><span>runs ${esc(p.trig)}${p.rec?' / recommended':''}</span></span><input class="ck-box" type="checkbox" data-act="wz-play" value="${esc(p.title)}"${w.plays.includes(p.title)?' checked':''} aria-label="${esc(p.title)}"></label>`).join('')}</div>`;}
  if(w.step===4)body=`<h2>Decide what needs a person.</h2><p class="v-sub">Anything on this list waits for your OK before it goes out.</p>${rulesHTML(w.rules,'wz')}`;
  if(w.step===5)body=`<h2>Ready to start your engines.</h2>
    <dl class="kv"><dt>business</dt><dd>${esc(w.name||'Untitled')}</dd><dt>setup</dt><dd>${esc(s.name)}</dd><dt>plan</dt><dd>${esc(LIC[w.lic].name)} / ${esc(LIC[w.lic].price)} a month</dd><dt>engines</dt><dd><span class="etags">${w.engines.map(tag).join('')}</span></dd><dt>automations</dt><dd>${(w.plays||[]).length} on</dd><dt>tools</dt><dd>${Object.keys(w.conns).filter(k=>w.conns[k]).join(', ')||'none yet'}</dd></dl>
    <pre class="boot" id="boot" aria-live="polite">${w.booted?'':'Waiting to start'}</pre>`;
  const last=w.step===5;
  return head('setup','Set up your business','Six quick steps and your engines are running.')+steps+`<div class="wz-body">${body}<div class="wz-nav"><button class="btn ghost" type="button" data-act="wz-back"${w.step?'':' disabled'}>Back</button><button class="btn" type="button" data-act="${last?'wz-go':'wz-next'}">${last?'Start engines':'Next'}</button></div></div>`;
}
function rulesHTML(r,p){
  const R=[['newClient','First message to a new client or lead','Every first reply waits for you.'],['money','Anything that spends or charges money','Purchase orders, refunds and charges over the limit.'],['contracts','Contracts, terms and pricing','Anything that commits the business.'],['bulk','Messages to more than 20 people','Newsletters, investor updates and announcements.'],['refunds','Refunds and credits','Always ask before money goes back out.']];
  return `<div class="rules">${R.map(([k,t,s])=>`<div class="rule"><span class="r-t"><b>${t}</b><span>${s}</span></span>${k==='money'?`<label class="fl" style="gap:4px"><span class="label">over $</span><input class="inp" type="number" min="0" step="50" data-act="${p}-amt" value="${r.amt}" aria-label="Money limit"></label>`:''}<button class="sw" type="button" role="switch" aria-checked="${!!r[k]}" data-act="${p}-rule" data-k="${k}" aria-label="${esc(t)}"></button></div>`).join('')}</div>`;
}
function wzNext(){
  const w=ui.wz;
  if(w.step===0){const n=($('#wz-name')||{}).value||'';w.name=n.trim();w.owner=(($('#wz-owner')||{}).value||'').trim();if(!w.name){toast('Add a business name to continue.');$('#wz-name').focus();return;}}
  if(w.step===1){const need=TIER.indexOf(w.lic)+1;if(w.engines.length!==need){toast(`Pick exactly ${need} engine${need>1?'s':''} for ${LIC[w.lic].name}.`);return;}w.plays=null;}
  w.step=Math.min(5,w.step+1);render();
}
async function wzGo(){
  const w=ui.wz,s=wzSetup(),b=$('#boot');if(w.booting)return;w.booting=true;
  const dots=(k,v)=>'  '+k+' '+'.'.repeat(Math.max(3,18-k.length))+' <b>'+v+'</b>';
  const lines=['Setting up '+esc(w.name),dots('plan',LIC[w.lic].name.toLowerCase())].concat(w.engines.map(e=>dots(ENGN[e].name,'running'))).concat([dots('automations',(w.plays||[]).length+' on'),dots('your OK',(Object.keys(w.rules).filter(k=>k!=='amt'&&w.rules[k]).length)+' rules on'),'Ready']);
  const sl=ms=>new Promise(r=>setTimeout(r,RM?0:ms));
  b.innerHTML='';for(const l of lines){b.innerHTML+=(b.innerHTML?'\n':'')+l;await sl(240);}
  await sl(500);
  S=init(w.type,{biz:w.name,owner:w.owner||null,engines:w.engines,license:w.lic,plays:w.plays,conns:w.conns,rules:w.rules});
  S.log=[];pushLog('@'+w.engines[0],'started with '+w.engines.length+' engine'+(w.engines.length>1?'s':''),'ready');
  save();ui.wz=null;toast('Engines started for '+S.biz+'.');location.hash='overview';
}

/* ---------- settings ---------- */
function vSettings(){
  const T=[['team','Team'],['license','Plan'],['tools','Tools'],['rules','Approvals'],['data','Your data']];
  let body='';
  if(ui.setTab==='team')body=`<div class="set-card"><h2>Team</h2><div class="tbl-w"><table class="tbl" style="min-width:420px"><thead><tr><th>Name</th><th>Role</th><th>Can approve</th></tr></thead><tbody>${S.people.map((p,i)=>`<tr><td class="n">${esc(p.name)}</td><td><select class="dd" data-act="role" data-i="${i}">${['Owner','Admin','Approver','Member'].concat([p.role]).filter((v,j,a)=>a.indexOf(v)===j).map(r=>`<option${r===p.role?' selected':''}>${esc(r)}</option>`).join('')}</select></td><td>${/Owner|Admin|Approver|Founder/.test(p.role)?'yes':'no'}</td></tr>`).join('')}</tbody></table></div>
    <div class="invite"><input class="inp" id="inv-name" placeholder="Name or email" autocomplete="off"><select class="dd" id="inv-role"><option>Member</option><option>Approver</option><option>Admin</option></select><button class="btn" type="button" data-act="invite">Invite</button></div></div>`;
  if(ui.setTab==='license'){const L=LIC[S.license];body=`<div class="set-card"><h2>${esc(L.name)} / ${esc(L.price)} a month</h2><p class="v-sub">${S.licensed.length} of 3 engines. Hosting, fixes and updates included.</p>
    <div class="g g3">${ENG.map(e=>`<div class="cell etile e-${e.id}${has(e.id)?'':' locked'}"><div class="et-top"><span class="label">@${e.id}</span>${has(e.id)?'<span class="state on">included</span>':'<span class="state lock">not included</span>'}</div><div class="et-name">${esc(e.name)}</div>${has(e.id)?'':`<button class="btn btn-xs" type="button" data-act="lic-add" data-e="${e.id}">Add ${esc(e.name)}</button>`}</div>`).join('')}</div></div>
    <div class="set-card"><h2>Resale license</h2><p class="v-sub">Not active. If the ${esc(setup().name)} works for you, a resale license lets you sell it to businesses like yours. We keep it running for every customer you sign.</p><div class="v-actions"><a class="btn ghost" href="start.html#resale">Ask about resale</a></div></div>`;}
  if(ui.setTab==='tools')body=`<div class="set-card"><h2>Tools</h2><div class="conn">${S.integrations.map((t,i)=>`<div class="${t.on?'on':''}"><span class="cn-ic">${esc(t.n[0])}</span><span class="cn-n">${esc(t.n)}</span><span class="cn-s">${t.on?'connected':''}</span><button class="btn ${t.on?'ghost ':''}btn-xs" type="button" data-act="tool" data-i="${i}">${t.on?'Disconnect':'Connect'}</button></div>`).join('')}</div></div>`;
  if(ui.setTab==='rules')body=`<div class="set-card"><h2>What needs your OK</h2><p class="v-sub">Anything that matches one of these waits for you first. Each automation can also check with you on its own.</p>${rulesHTML(S.rules,'set')}</div>`;
  if(ui.setTab==='data')body=`<div class="set-card"><h2>Your data</h2><p class="v-sub">We own the software. Your business data is yours, and you can download all of it any time.</p><div class="v-actions"><button class="btn ghost" type="button" data-act="export">Export all data</button><button class="btn ghost" type="button" data-act="reset">Reset this demo</button></div></div>`;
  return head('settings','Settings','Your team, plan, tools and what needs your OK.')+`<div class="tabs filters stabs" role="tablist" aria-label="Settings">${T.map(([k,t])=>`<button class="tab" type="button" role="tab" data-act="set-tab" data-t="${k}" aria-selected="${ui.setTab===k}" aria-pressed="${ui.setTab===k}">${t}</button>`).join('')}</div>${body}`;
}

/* ---------- drawer ---------- */
function openDrawer(html){
  closeDrawer(true);
  const root=$('#drawer-root');root.innerHTML=`<div class="drawer-scrim" data-act="dr-close"></div><aside class="drawer" role="dialog" aria-modal="true" aria-labelledby="dr-t">${html}</aside>`;
  const d=$('.drawer',root);requestAnimationFrame(()=>requestAnimationFrame(()=>d.classList.add('open')));
  drawer=document.activeElement;setTimeout(()=>{const f=$('[data-act="dr-close"].lnk',root);if(f)f.focus();},60);
}
function closeDrawer(quick){const root=$('#drawer-root');if(!root||!root.firstChild)return;const d=$('.drawer',root);if(quick||RM){root.innerHTML='';}else{d.classList.remove('open');setTimeout(()=>{root.innerHTML='';},260);}if(drawer&&drawer.focus&&!quick)drawer.focus();}
function leadDrawer(id){
  const l=S.leads.find(x=>x.id===id);if(!l)return;
  const tl=[['@leads',`came in from ${l.src}`,'2 days ago']];
  if(l.stage!=='New')tl.push(['@agents','first reply sent after your approval','2 days ago']);
  if(['Booked','Won'].includes(l.stage))tl.push(['@ops','call booked and added to the calendar','yesterday']);
  if(l.stage==='Won')tl.push(['you','marked won',l.last]);
  if(l.stage==='Lost')tl.push(['@agents','no reply after 3 follow-ups',l.last]);
  openDrawer(`<div class="dr-hd"><span class="label">lead</span><button class="lnk" type="button" data-act="dr-close">close &times;</button></div><div class="dr-bd">
  <h2 class="dr-t" id="dr-t">${esc(l.n)}</h2>
  <dl class="kv"><dt>source</dt><dd>${esc(l.src)}</dd><dt>value</dt><dd>${money(l.val)}</dd><dt>owner</dt><dd>${esc(l.owner)}</dd><dt>stage</dt><dd><select class="dd" data-act="lead-stage" data-id="${l.id}">${STAGES.map(s=>`<option${s===l.stage?' selected':''}>${s}</option>`).join('')}</select></dd></dl>
  <p class="label">timeline</p><ul class="tl">${tl.map(([a,m,t])=>`<li class="${actorCls(a).trim()}"><span>${esc(WHO[a]||a)} / ${esc(t)}</span>${esc(m)}</li>`).join('')}</ul>
  <div class="v-actions"><button class="btn" type="button" data-act="lead-follow" data-id="${l.id}">Draft a follow-up</button><button class="btn ghost" type="button" data-act="lead-won" data-id="${l.id}">Mark won</button></div></div>`);
}
function recDrawer(id){
  const r=S.records.find(x=>x.id===id);if(!r)return;
  const rel=S.log.filter(x=>x.m.toLowerCase().includes(first(r.n).toLowerCase())).slice(-5).reverse();
  openDrawer(`<div class="dr-hd"><span class="label">${esc(r.kind)}</span><button class="lnk" type="button" data-act="dr-close">close &times;</button></div><div class="dr-bd">
  <h2 class="dr-t" id="dr-t">${esc(r.n)}</h2><dl class="kv"><dt>type</dt><dd>${esc(r.kind)}</dd><dt>status</dt><dd>${esc(r.status)}</dd><dt>owner</dt><dd>${esc(r.owner)}</dd><dt>updated</dt><dd>${esc(r.upd)}</dd></dl>
  <p class="label">related activity</p>${rel.length?`<div class="feed" style="padding:0">${rel.map(rowHTML).join('')}</div>`:'<p class="v-sub" style="font-size:14px">Nothing logged against this record today.</p>'}
  <p class="note">Your engines update records and note every change.</p></div>`);
}

/* ================= render + routing ================= */
const VIEWS={overview:vOverview,approvals:vApprovals,activity:vActivity,engines:vEngines,'engine-ops':()=>vEngine('ops'),'engine-agents':()=>vEngine('agents'),'engine-leads':()=>vEngine('leads'),plays:vPlays,pipeline:vPipeline,records:vRecords,score:vScore,setup:vSetup,settings:vSettings};
function render(keepScroll){
  renderSide();setCrumb();
  const v=$('#view');const y=window.scrollY;
  v.innerHTML=VIEWS[route]();
  decode($('.v-title',v));
  if(keepScroll)window.scrollTo(0,y);
  document.title=($('.v-title',v)?$('.v-title',v).getAttribute('aria-label')||$('.v-title',v).textContent:'Console')+' | OpLev Console';
}
function onRoute(){
  const h=(location.hash||'').slice(1).toLowerCase();
  if(SET[h]){S=init(h);save();ui.apSel=null;ui.wz=null;try{history.replaceState(null,'','#overview');}catch(e){}route='overview';render();window.scrollTo(0,0);toast('Opened the '+SET[h].name+' demo.');return;}
  const next=VIEWS[h]?h:'overview';
  const changed=next!==route;route=next;closeDrawer(true);
  document.querySelector('.app').classList.remove('side-open');
  render();if(changed)window.scrollTo(0,0);
}

/* live inserts without re-rendering the view */
function liveInsert(x){
  const n=S.approvals.length;
  $$('[data-k="ap-count"]').forEach(el=>el.textContent=n);
  const b=$('#ap-badge');if(b){b.textContent=n;b.dataset.n=n;}
  if(/^@/.test(x.a))$$(`[data-k="count-${x.a.slice(1)}"]`).forEach(el=>el.textContent=S.counts[x.a.slice(1)]);
  $$('.feed[data-live]').forEach(f=>{
    if(f.dataset.engine&&x.a!=='@'+f.dataset.engine)return;
    if(f.hasAttribute('data-filter')&&!filteredLog().includes(x))return;
    const empty=$('.feed-empty',f);if(empty)empty.remove();
    f.insertAdjacentHTML('afterbegin',rowHTML(x));
    const max=+f.dataset.max||14;while(f.children.length>max)f.lastElementChild.remove();
  });
  const c=$('#act-count');if(c)c.textContent=filteredLog().length+' events';
}

/* ================= live simulation ================= */
function tick(){
  if(!S||!S.live||document.hidden)return;
  const active=S.licensed.filter(e=>S.running[e]);if(!active.length)return;
  const s=setup(),pool=s.demo.feed.filter(f=>active.includes(f[0].slice(1)));if(!pool.length)return;
  S.tick=(S.tick||0)+1;
  const [a,m,r]=pool[Math.floor(Math.random()*pool.length)];
  const plays=S.plays.filter(p=>p.e===a.slice(1)&&p.added&&p.on);
  if(plays.length){const p=plays[Math.floor(Math.random()*plays.length)];p.runs++;p.last='just now';}
  pushLog(a,m,r);
  if(S.tick%5===0&&S.approvals.length<6&&has('agents')&&S.running.agents){
    const l=S.leads[Math.floor(Math.random()*S.leads.length)];
    S.approvals.unshift({id:nid(),e:'agents',kind:'Reply to a lead',to:l.n,why:'First message to a new contact',age:'just now',draft:`Hi ${first(l.n)}, thanks for getting in touch with ${S.biz}. Happy to help. Do you have 15 minutes this week? Here are a few times that work: Tuesday 10:00, Wednesday 2:30 or Thursday 9:00.\n\n${first(owner())}, ${S.biz}`});
    pushLog('@agents','drafted a reply to '+l.n,'waiting on you');
    if(route==='approvals'){const L=$('#ap-list');if(L)L.innerHTML=apList();else render(true);}
    if(route==='overview'&&!(document.activeElement||document.body).closest('#view input,#view textarea,#view select'))render(true);
  }
  save();
}

/* ================= toast ================= */
let toastT=0;
function toast(msg){const r=$('#toast-root');r.innerHTML=`<div class="toast" role="status">${esc(msg)}</div>`;clearTimeout(toastT);toastT=setTimeout(()=>{r.innerHTML='';},2800);}

/* ================= actions ================= */
const ACT={
  'side-open'(){$('.app').classList.add('side-open');},
  'side-close'(){$('.app').classList.remove('side-open');},
  ws(el){const m=$('#ws-menu');const open=m.hidden;m.hidden=!open;el.setAttribute('aria-expanded',String(open));},
  'ws-pick'(el){location.hash=el.dataset.id;},
  reset(){S=init(S.type);ui.apSel=null;ui.wz=null;save();toast('Demo reset.');location.hash='overview';render();},
  go(el){location.hash=el.dataset.r;},
  live(){S.live=!S.live;save();renderSide();toast(S.live?'Live activity resumed.':'Live activity paused.');},
  'ap-go'(el){ui.apSel=el.dataset.id;},
  'ap-sel'(el){ui.apSel=el.dataset.id;$$('.ap-item').forEach(b=>b.setAttribute('aria-current',String(b.dataset.id===ui.apSel)));$('#ap-detail').innerHTML=apDetail();if(innerWidth<1000)$('#ap-detail').scrollIntoView({block:'start',behavior:RM?'auto':'smooth'});},
  'ap-ok'(el){const a=S.approvals.find(x=>x.id===el.dataset.id);if(!a)return;const t=$('#ap-draft');if(t)a.draft=t.value;
    S.approvals=S.approvals.filter(x=>x!==a);ui.apSel=null;pushLog('you','approved '+a.kind.toLowerCase()+' for '+a.to,'ok','me');pushLog('@'+a.e,'sent '+a.kind.toLowerCase()+' to '+a.to,'sent');save();render(true);toast('Approved. Sent to '+a.to+'.');},
  'ap-no'(el){const a=S.approvals.find(x=>x.id===el.dataset.id);if(!a)return;S.approvals=S.approvals.filter(x=>x!==a);ui.apSel=null;pushLog('you','rejected '+a.kind.toLowerCase()+' for '+a.to,'nothing sent','me');save();render(true);toast('Rejected. Nothing was sent.');},
  'act-f'(el){ui.actF=el.dataset.f;render(true);},
  'act-pre'(el){ui.actF=el.dataset.f;},
  'play-f'(el){ui.playF=el.dataset.f;render(true);},
  'go-plays'(el){ui.playF=el.dataset.e;location.hash='plays';},
  'play-add'(el){const p=S.plays.find(x=>x.id===el.dataset.id);if(!p||!has(p.e))return;p.added=true;p.on=true;pushLog('you','added '+p.title.toLowerCase()+' to '+ENGN[p.e].name,'added','me');save();render(true);toast(p.title+' added to '+ENGN[p.e].name+'.');},
  'play-on'(el){const p=S.plays.find(x=>x.id===el.dataset.id);if(!p)return;p.on=!p.on;pushLog('you',(p.on?'turned on ':'turned off ')+p.title.toLowerCase(),p.on?'on':'off','me');save();render(true);},
  'play-run'(el){const p=S.plays.find(x=>x.id===el.dataset.id);if(!p)return;p.runs++;p.last='just now';pushLog('@'+p.e,'ran '+p.title.toLowerCase()+' on request','done');save();render(true);toast(p.title+' ran.');},
  'eng-run'(el){const e=el.dataset.e;S.running[e]=!S.running[e];pushLog('you',(S.running[e]?'resumed ':'paused ')+ENGN[e].name,S.running[e]?'running':'paused','me');save();render(true);},
  'lic-add'(el){const e=el.dataset.e;if(has(e))return;S.licensed.push(e);S.license=TIER[Math.min(2,S.licensed.length-1)];S.running[e]=true;S.counts[e]=0;
    S.plays.filter(p=>p.e===e).slice(0,3).forEach(p=>{p.added=true;p.on=true;});pushLog('@'+e,ENGN[e].name+' engine started','running');save();render(true);toast(ENGN[e].name+' added. Your plan is now '+LIC[S.license].name+', '+LIC[S.license].price+' a month.');},
  'pipe-f'(el){ui.pipeF=el.dataset.f;render(true);},
  'lead-open'(el){leadDrawer(el.dataset.id);},
  'rec-open'(el){recDrawer(el.dataset.id);},
  'dr-close'(){closeDrawer();},
  'lead-follow'(el){const l=S.leads.find(x=>x.id===el.dataset.id);if(!l)return;
    if(!has('agents')){toast('Add the Agents engine to draft follow-ups.');return;}
    S.approvals.unshift({id:nid(),e:'agents',kind:'Follow-up',to:l.n,why:'You asked for a follow-up draft',age:'just now',draft:`Hi ${first(l.n)}, following up on your note to ${S.biz}. Is this still something you're looking at? I can hold a time for you this week.\n\n${first(owner())}`});
    pushLog('@agents','drafted a follow-up to '+l.n,'waiting on you');save();closeDrawer();render(true);toast('Draft ready in Approvals.');},
  'lead-won'(el){const l=S.leads.find(x=>x.id===el.dataset.id);if(!l)return;l.stage='Won';l.last='just now';pushLog('you','marked '+l.n+' won',money(l.val),'me');save();closeDrawer();render(true);toast(l.n+' marked won.');},
  'set-tab'(el){ui.setTab=el.dataset.t;render(true);},
  invite(){const n=$('#inv-name'),r=$('#inv-role');const v=(n.value||'').trim();if(!v){n.focus();toast('Add a name or email.');return;}S.people.push({name:v,role:r.value});pushLog('you','invited '+v+' as '+r.value.toLowerCase(),'invited','me');save();render(true);toast('Invite sent to '+v+' (sample).');},
  tool(el){const t=S.integrations[+el.dataset.i];if(!t)return;t.on=!t.on;pushLog('you',(t.on?'connected ':'disconnected ')+t.n,t.on?'connected':'off','me');save();render(true);},
  'set-rule'(el){const k=el.dataset.k;S.rules[k]=!S.rules[k];save();render(true);},
  'wz-rule'(el){const k=el.dataset.k;ui.wz.rules[k]=!ui.wz.rules[k];render(true);},
  export(){toast('In the live product this emails you a full export.');},
  'wz-next'(){wzNext();},
  'wz-back'(){if(ui.wz.step>0){ui.wz.step--;render(true);}},
  'wz-conn'(el){const n=el.dataset.n;ui.wz.conns[n]=!ui.wz.conns[n];render(true);},
  'wz-go'(){wzGo();}
};
const CHANGE={
  'play-trig'(el){const p=S.plays.find(x=>x.id===el.dataset.id);if(!p)return;p.trig=el.value;pushLog('you',p.title.toLowerCase()+' now runs '+el.value,'saved','me');save();},
  'play-appr'(el){const p=S.plays.find(x=>x.id===el.dataset.id);if(!p)return;p.appr=el.checked;pushLog('you',(p.appr?'asked to check first on ':'stopped checking first on ')+p.title.toLowerCase(),'saved','me');save();},
  'lead-stage'(el){const l=S.leads.find(x=>x.id===el.dataset.id);if(!l)return;l.stage=el.value;l.last='just now';pushLog('you','moved '+l.n+' to '+l.stage.toLowerCase(),'saved','me');save();render(true);},
  role(el){const p=S.people[+el.dataset.i];if(p){p.role=el.value;save();render(true);}},
  'set-amt'(el){S.rules.amt=Math.max(0,+el.value||0);save();},
  'wz-amt'(el){ui.wz.rules.amt=Math.max(0,+el.value||0);},
  'wz-type'(el){ui.wz.type=el.value;const s=SET[el.value];ui.wz.engines=s.engines.slice();ui.wz.lic=s.license;ui.wz.plays=null;const n=$('#wz-name');if(n)ui.wz.name=n.value;const o=$('#wz-owner');if(o)ui.wz.owner=o.value;render(true);},
  'wz-lic'(el){const w=ui.wz;w.lic=el.value;const need=TIER.indexOf(w.lic)+1;const rec=SET[w.type].engines.concat(ENG.map(e=>e.id)).filter((v,i,a)=>a.indexOf(v)===i);w.engines=rec.slice(0,need);render(true);},
  'wz-eng'(el){const w=ui.wz;const need=TIER.indexOf(w.lic)+1;if(el.checked){if(w.engines.length>=need){w.engines.shift();}w.engines.push(el.value);}else w.engines=w.engines.filter(e=>e!==el.value);render(true);},
  'wz-play'(el){const w=ui.wz;if(!w.plays)w.plays=[];if(el.checked){if(!w.plays.includes(el.value))w.plays.push(el.value);}else w.plays=w.plays.filter(t=>t!==el.value);}
};

/* ================= boot ================= */
function boot(){
  shell();
  S=load()||init('clinic');
  document.addEventListener('click',e=>{
    const el=e.target.closest('[data-act]');
    const wsm=$('#ws-menu');if(wsm&&!wsm.hidden&&!e.target.closest('#ws')){wsm.hidden=true;$('.ws-btn').setAttribute('aria-expanded','false');}
    if(!el||!ACT[el.dataset.act])return;
    if(el.tagName==='SELECT'||(el.tagName==='INPUT'&&el.type!=='button'))return;
    if(el.tagName==='LABEL')return;
    if(el.tagName==='A'&&el.getAttribute('href')&&el.dataset.act!=='ap-go'&&el.dataset.act!=='act-pre')e.preventDefault();
    ACT[el.dataset.act](el,e);
  });
  document.addEventListener('change',e=>{const el=e.target.closest('[data-act]');if(el&&CHANGE[el.dataset.act])CHANGE[el.dataset.act](el,e);});
  document.addEventListener('input',e=>{
    if(e.target.id==='act-q'){ui.actQ=e.target.value;const f=$('.feed[data-filter]');if(f)f.innerHTML=feedRows(filteredLog(),200);const c=$('#act-count');if(c)c.textContent=filteredLog().length+' events';}
    if(e.target.id==='rec-q'){ui.recQ=e.target.value;const q=ui.recQ.trim().toLowerCase();$('#rec-body').innerHTML=recRows(S.records.filter(r=>!q||(r.n+' '+r.kind+' '+r.status+' '+r.owner).toLowerCase().includes(q)));}
    if(e.target.id==='wz-name')ui.wz.name=e.target.value;
    if(e.target.id==='wz-owner')ui.wz.owner=e.target.value;
  });
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if($('#drawer-root').firstChild)closeDrawer();$('.app').classList.remove('side-open');const m=$('#ws-menu');if(m&&!m.hidden)m.hidden=true;}
    if((e.key==='Enter'||e.key===' ')&&e.target.matches('tr.click')){e.preventDefault();ACT[e.target.dataset.act](e.target);}
  });
  window.addEventListener('hashchange',onRoute);
  const clk=()=>{const el=$('#clk');if(el){const d=new Date();el.textContent=pad2(d.getHours())+':'+pad2(d.getMinutes());}};clk();setInterval(clk,10000);
  setInterval(tick,6500);
  onRoute();
}
boot();
})();
