import {cash,el,grid,head,pill,reason,text} from './format.js';
import {optimizer,rulesGrid} from './coupon-grid.js';

let result=null, archived=null, selected='', revision=0, custom=false;
const tabs=[...document.querySelectorAll('nav a')];
const feedback=message=>{el('#feedback').textContent=message;};
const current=()=>tabs.find(tab=>tab.hash===location.hash)||tabs[0];

async function query(path, payload) {
  const response = await fetch(path,payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const data=await response.json();
  if(!response.ok) throw new Error(data.message||'复核请求失败');
  return data;
}

function view(key,sale,picker) {
  const d=result[key];
  const q=sale&&result.eligibility[sale.id];
  const refundRows=rows=>grid(['退单','原单','交易日','退单日','应退 / 状态'],rows.map(row=>[row.id,row.order,row.sale_day,row.return_day,row.status==='posted'?cash(row.expected):reason(row.reason)]),[4]);
  switch(key){
    case 'receipts':
      return [head('流水采信')+grid(['行号','业务键','状态'],d.rows.map(row=>[row.line,row.id,reason(row.code)])),head('需要复核的来源')+grid(['行号','业务键','原因'],d.rows.filter(row=>row.code!=='ACCEPTED').map(row=>[row.line,row.id,reason(row.code)]))];
    case 'versions':
      return [head('生效版本')+grid(['规则','版本','作用范围'],d.versions.map(rule=>[rule.code,rule.version,[...rule.shops,...rule.categories].join('、')||'通用'])),head('并发生效')+grid(['券号','并发版本','起始 UTC'],d.conflicts.map(row=>[row.code,row.versions.join(' / '),row.start]))];
    case 'eligibility':
      return [head('小票用券资格',picker)+grid(['券号','判定','原价基数'],(q?.findings||[]).map(row=>[row.coupon,reason(row.reason),cash(row.eligible_gross)]),[2]),head('许可方阵')+rulesGrid(q)];
    case 'refunds':
      return [head('退货原摊流水')+refundRows(d.filter(r=>r.status==='posted')),head('退货隔离')+refundRows(d.filter(r=>r.status==='isolated'))];
    case 'reconcile':
      return [head('逐笔实收差异',pill(d.status==='MATCHED'?'总额对平':'存在差异',d.status==='MATCHED'?'good':'bad'))+grid(['业务键','来源行','差异','金额'],d.differences.map(x=>[x.id,x.source_line,reason(x.reason),cash(x.gap)]),[3]),head('分摊守恒')+grid(['小票','明细','原分摊实付','已退','未退'],d.lines.map(x=>[x.order,x.line,cash(x.actual),cash(x.refunded),cash(x.retained)]),[2,3,4])];
    case 'trace': {
      const packet=d.packets.find(row=>row.order===sale?.id);
      const control=archived?`<p class="hash">${text(archived.id)}</p><div class="tags"><button id="rerun">核验重算</button></div><a class="download" href="/api/runs/${archived.id}/export">导出追溯联单</a>`:'<p>保存联单后可导出</p>';
      return [head('原票与退单',picker)+(packet?`<div class="tags">${pill(`原小票第 ${packet.receipt_line} 行`)}</div>${refundRows(packet.returns)}`:'<p>没有该单投递凭证</p>'),head('归档联单')+control];
    }
    default: return optimizer(sale,q,picker);
  }
}

function paint() {
  if(!result)return;
  const tab=current();
  tabs.forEach(node=>node===tab?node.setAttribute('aria-current','page'):node.removeAttribute('aria-current'));
  el('#section-title').textContent=tab.textContent;
  const totals=result.reconcile.totals;
  el('#figures').innerHTML=[['商品毛额',totals.gross],['实摊优惠',totals.discount],['复算实付',totals.due],['应冲退款',totals.refunded]].map(([label,value])=>`<div class="kpi">${label}<strong>${cash(value)}</strong></div>`).join('');
  const sale=result.optimizer.find(row=>row.id===selected)||result.optimizer[0];
  const picker=`<select id="receipt" aria-label="选择小票">${result.optimizer.map(row=>`<option ${row===sale?'selected':''}>${text(row.id)}</option>`).join('')}</select>`;
  const panels=view(tab.dataset.panel,sale,picker);
  el('#receipt-panel').innerHTML=panels[0]; el('#matrix-panel').innerHTML=panels[1];
  el('#snapshot').textContent=archived?`${archived.manifest.rule_version} · ${archived.id.slice(0,12)}`:'retail-promo-1.0 · 样例预览';
}

async function load() {
  const seq=++revision, sample=el('#sample').value;
  feedback('读取交易中');
  try {
    const data=await query(`/api/samples/${sample}`);
    if(seq!==revision)return;
    result=data;archived=null;selected='';custom=false;paint();
    feedback(result.reconcile.status==='MATCHED'?'交易与退款已对平':'发现实收差异');
  }catch(error){if(seq===revision)feedback(error.message);}
}

async function save(payload){
  const seq=++revision;
  el('#archive').disabled=true;
  try{
    const record=await query('/api/runs',payload);
    if(seq!==revision)return;
    archived=record;result=record.result;custom=!payload.sample;paint();
    feedback(record.reused?'同一批次已归档':'联单已归档');
  }catch(error){if(seq===revision)feedback(error.message);}
  finally{el('#archive').disabled=custom;}
}

el('#sample').addEventListener('change',()=>{el('#archive').disabled=false;load();});
el('#archive').addEventListener('click',()=>save({sample:el('#sample').value}));
el('#source-form').addEventListener('submit',event=>{
  event.preventDefault();
  try{save({events:el('#events').value,rules:JSON.parse(el('#rules').value)});}
  catch{feedback('规则集需为有效 JSON');}
});
document.addEventListener('change',event=>{if(event.target.id==='receipt'){selected=event.target.value;paint();el('#receipt').focus();}});
document.addEventListener('click',async event=>{
  if(event.target.id==='rerun'&&archived){
    try{await query(`/api/runs/${archived.id}/rerun`,{});feedback('重算与联单一致');}
    catch(error){feedback(error.message);}
  }
});
window.addEventListener('hashchange',paint);
load();
