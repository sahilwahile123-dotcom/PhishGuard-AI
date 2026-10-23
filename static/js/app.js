const $ = id => document.getElementById(id);
const charts = {};
const LABELS = {url_length:"URL length", host_length:"Host length", path_length:"Path length", query_length:"Query length", has_ip:"IP address as host", is_https:"Uses HTTPS", num_subdomains:"Subdomains", num_dots:"Dots", num_hyphens:"Hyphens", num_digits:"Digits", digit_ratio:"Digit ratio", num_special_chars:"Special characters (? = & % _ ~ # $ ! *)", has_at:"Contains @", is_shortener:"URL shortener", unusual_port:"Unusual port", keyword_count:"Bait keywords (login, verify...)", host_entropy:"Host randomness (entropy)"};
const FLAG = {url_length:v=>v>75, has_ip:v=>v, is_https:v=>!v, num_subdomains:v=>v>=3, num_hyphens:v=>v>=3, has_at:v=>v, is_shortener:v=>v, unusual_port:v=>v, keyword_count:v=>v>=2, num_special_chars:v=>v>=5};
const yn = new Set(["has_ip","is_https","has_at","is_shortener","unusual_port"]);

function setStatus(msg, cls=""){ const s=$("status"); s.textContent=msg; s.className="status "+cls; }
function draw(id, cfg){ if(charts[id]) charts[id].destroy(); charts[id]=new Chart($(id), cfg); }
const axis = {ticks:{color:"#93a5c7"},grid:{color:"rgba(120,170,255,.12)"}};
const opts = {plugins:{legend:{labels:{color:"#93a5c7"}}},scales:{x:axis,y:axis}};

function validate(v){
  v=v.trim();
  if(!v) return "Enter a URL first.";
  if(/\s/.test(v)) return "A URL cannot contain spaces.";
  if(v.length>2048) return "That URL is too long (max 2048 characters).";
  if(/^[a-z][a-z0-9+.-]*:\/\//i.test(v) && !/^https?:\/\//i.test(v)) return "Only http:// and https:// URLs are supported.";
  return null;
}
function showResult(d){
  $("result").hidden=false;
  $("verdict").textContent=d.classification; $("verdict").className="verdict v-"+d.classification;
  $("confidence").textContent = d.show_confidence ? `Model phishing probability: ${(d.phishing_probability*100).toFixed(1)}% (model evaluated on a held-out test set; errors still occur).` : "Confidence hidden: this model has no saved evaluation metrics.";
  $("featRows").innerHTML = Object.entries(d.features).map(([k,v])=>{
    const f = FLAG[k] && FLAG[k](v); const shown = yn.has(k) ? (v?"Yes":"No") : v;
    return `<tr><td>${LABELS[k]}</td><td>${shown}</td><td class="${f?"flag":""}">${f?"Heuristic warning sign":"-"}</td></tr>`;}).join("");
  const keys=["url_length","host_length","path_length","num_dots","num_hyphens","num_digits","num_special_chars","keyword_count"];
  draw("featChart",{type:"bar",data:{labels:keys.map(k=>LABELS[k].split(" (")[0]),datasets:[{label:"Count",data:keys.map(k=>d.features[k]),backgroundColor:"#22d3ee"}]},options:opts});
}
$("scanForm").addEventListener("submit", async e=>{
  e.preventDefault();
  const url=$("urlInput").value, err=validate(url);
  if(err){ setStatus(err,"error"); return; }
  $("scanBtn").disabled=true; $("result").hidden=true; setStatus("Analysing URL text...","loading");
  try{
    const r=await fetch("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url})});
    const d=await r.json();
    if(!r.ok){ setStatus(d.error||"Request failed.","error"); }
    else { setStatus("Done. The URL was analysed as text only; it was never opened."); showResult(d); }
  }catch{ setStatus("Cannot reach the server. Is the Flask app running?","error"); }
  $("scanBtn").disabled=false;
  $("scanner").scrollIntoView({behavior:"smooth"});
});
$("clearBtn").addEventListener("click",()=>{ $("urlInput").value=""; $("result").hidden=true; setStatus("Enter a URL above to begin."); $("urlInput").focus(); });

async function loadModelInfo(){
  try{
    const d=await (await fetch("/api/model-info")).json();
    if(!d.model_ready||!d.metrics){ $("modelNote").textContent=d.message||"No evaluation metrics yet. Train the model to see real results."; return; }
    const m=d.metrics, imp=Object.entries(m.feature_importances).sort((a,b)=>b[1]-a[1]).slice(0,10);
    draw("impChart",{type:"bar",data:{labels:imp.map(i=>LABELS[i[0]].split(" (")[0]),datasets:[{label:"Importance",data:imp.map(i=>i[1]),backgroundColor:"#3b82f6"}]},options:{...opts,indexAxis:"y"}});
    draw("distChart",{type:"doughnut",data:{labels:["Legitimate","Phishing"],datasets:[{data:[m.test_class_counts.legitimate,m.test_class_counts.phishing],backgroundColor:["#34d399","#f87171"]}]},options:{plugins:opts.plugins}});
    draw("metChart",{type:"bar",data:{labels:["Accuracy","Precision","Recall","F1"],datasets:[{label:"Test set score",data:[m.accuracy,m.precision,m.recall,m.f1],backgroundColor:"#22d3ee"}]},options:{...opts,scales:{x:axis,y:{...axis,min:0,max:1}}}});
    const [[tn,fp],[fn,tp]]=m.confusion_matrix;
    $("modelNote").textContent=`Trained on ${m.train_size} URLs, tested on ${m.test_size} unseen URLs (${m.dataset}). Confusion matrix: TN ${tn}, FP ${fp}, FN ${fn}, TP ${tp}.`;
  }catch{ $("modelNote").textContent="Could not load model information."; }
}
loadModelInfo();
