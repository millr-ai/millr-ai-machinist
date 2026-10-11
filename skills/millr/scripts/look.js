// Look at a built Millr page: screenshots from headless Chromium, as many views as you ask for, from one browser launch.
//   node scripts/look.js review.html out.png [change index]                  one view
//   node scripts/look.js review.html shots/ all                               the overview and every change as drawn
//   node scripts/look.js review.html shots/ overview 0 3                      any views you name: overview, <i>
// Options: --jobs N (views open at once; default half the machine's cores, at least 1: software 3D shares the processor), --motion (play the camera's move instead of jumping to its last frame).
// Each view opens in its own fresh page, so it starts from the engineer's first view whatever order the views run in.
// The page says when a view has arrived and been checked (data-view="settled" on the stage), so nothing here sleeps for a fixed time;
// under reduced motion, which the page already supports, the camera jumps to the frame it would end on. Prints one line per view with the file, whether it settled, the time and every console error.
// Needs playwright-core and a Chromium it can launch (set CHROME to the executable, or let Playwright find its own; set NODE_PATH to the node_modules folder that holds playwright-core if it is not installed next to this script). The page carries three.js inside it and fetches nothing. If none of that is available where you are, say in the line after the receipt, in the engineer's words, that the page was not checked on screen, rather than guess.
let chromium;try{({chromium}=require('playwright-core'))}catch(e){console.error('look.js needs playwright-core (set NODE_PATH to the node_modules that holds it). Without it, use scripts/sheet.py, or say in the line after the receipt that the page was not checked on screen.');process.exit(2)}const path=require('path');const fs=require('fs');const os=require('os');
(async()=>{
  const argv=process.argv.slice(2),opt={jobs:Math.max(1,Math.floor(os.cpus().length/2)),motion:false},pos=[];
  for(let i=0;i<argv.length;i++){if(argv[i]==='--jobs')opt.jobs=Math.max(1,+argv[++i]||1);else if(argv[i]==='--motion')opt.motion=true;else pos.push(argv[i])}
  const [page,out,...rest]=pos;if(!page||!out){console.error('usage: node look.js review.html out.png [index]  |  node look.js review.html outdir/ all|overview|<i> ...');process.exit(1)}
  const single=/\.png$/i.test(out);
  let views=single?[{idx:rest[0]===undefined?null:+rest[0],file:out}]:null;
  const exe=process.env.CHROME;let b;
  try{b=await chromium.launch(Object.assign({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--no-sandbox']},exe?{executablePath:exe}:{}))}
  catch(e){console.error('No Chromium could be launched. Point CHROME at a Chromium or Chrome executable, or install Playwright\'s Chromium where downloads are allowed. Without a browser, the line after the receipt says the page was not checked on screen.');process.exit(2)}
  const ctx=await b.newContext({viewport:{width:1600,height:1000},deviceScaleFactor:1,reducedMotion:opt.motion?'no-preference':'reduce'});
  const url='file://'+path.resolve(page);
  const frames=(p,n=2)=>p.evaluate(n=>new Promise(r=>{const f=k=>k?requestAnimationFrame(()=>f(k-1)):r();f(n)}),n);
  async function shoot(v){
    const t0=Date.now(),p=await ctx.newPage(),errs=[];p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push('PAGEERROR '+e.message));
    let state='settled';
    try{
      await p.goto(url);
      await p.waitForFunction(()=>!document.getElementById('loading')||document.getElementById('stage').dataset.view==='no3d',null,{timeout:30000});   // the first frame is drawn (or the page has said 3D cannot start)
      const no3d=await p.evaluate(()=>document.getElementById('stage').dataset.view==='no3d');
      if(no3d)state='no 3D';
      else if(v.idx!==null){
        const n=await p.evaluate(()=>document.querySelectorAll('.finding .fhead').length);
        if(!(v.idx>=0&&v.idx<n))throw new Error(`there is no change ${v.idx}; the page has ${n} (0 to ${n-1})`);
        await p.evaluate(i=>document.querySelectorAll('.finding .fhead')[i].click(),v.idx);
        const signals=await p.evaluate(()=>!!document.getElementById('stage').dataset.view);
        if(signals){try{await p.waitForFunction(()=>document.getElementById('stage').dataset.view==='settled',null,{timeout:60000})}catch(e){state='did not settle in 60 s'}}
        else{state='older page, fixed wait';await p.waitForTimeout(opt.motion?2600:400)}
      }
      await frames(p);await p.screenshot({path:v.file});
    }catch(e){state='failed: '+e.message.split('\n')[0]}
    await p.close();
    console.log(`${path.basename(v.file)}  ${state}  ${((Date.now()-t0)/1000).toFixed(1)} s  errors: ${errs.length?JSON.stringify(errs):'none'}`);
    return state;
  }
  if(!single){
    fs.mkdirSync(out,{recursive:true});views=[];let n=null;
    for(const tok of rest.length?rest:['all']){
      if(tok==='overview')views.push({idx:null,file:path.join(out,'overview.png')});
      else if(tok==='all'){
        if(n===null){try{const line=fs.readFileSync(page,'utf8').split('\n').find(l=>l.startsWith('const REVIEW = '));const r=JSON.parse(line.slice(15).replace(/;\s*$/,''));const shown=f=>['cost','lead time','risk'].some(k=>['medium','high'].includes(String((f.flags||{})[k]||'').toLowerCase()));n=(r.blocking||[]).length+(r.improvements||[]).filter(shown).length}   // counted from the page's own data, so no page is drawn just to count
          catch(e){const p=await ctx.newPage();await p.goto(url);n=await p.evaluate(()=>document.querySelectorAll('.finding .fhead').length);await p.close()}}
        views.push({idx:null,file:path.join(out,'overview.png')});for(let i=0;i<n;i++)views.push({idx:i,file:path.join(out,`change-${i}.png`)});
      } else {const m=/^(\d+)$/.exec(tok);if(!m){console.error(`not a view: ${tok} (use overview, all or <i>)`);process.exit(1)}
        views.push({idx:+m[1],file:path.join(out,`change-${m[1]}.png`)})}
    }
  }
  const t0=Date.now(),queue=views.slice(),results=[];
  await Promise.all(Array.from({length:Math.min(opt.jobs,queue.length)},async()=>{while(queue.length)results.push(await shoot(queue.shift()))}));
  if(views.length>1)console.log(`${views.length} views in ${((Date.now()-t0)/1000).toFixed(1)} s`);
  await b.close();
})();
