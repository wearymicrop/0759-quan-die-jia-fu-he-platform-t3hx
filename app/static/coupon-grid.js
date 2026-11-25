import {cash, grid, head, pill, reason, text} from './format.js';

export function rulesGrid(qualification) {
  if (!qualification?.qualified.length) return '<p>该单没有可用券</p>';
  const codes = qualification.qualified.map(row=>row.code);
  const edge = (a,b) => qualification.matrix.find(item=>[item.a,item.b].includes(a)&&[item.a,item.b].includes(b));
  return `<div class="scroll gridbook" tabindex="0"><table aria-label="券对叠用方阵"><thead><tr><th>券对</th>${codes.map(k=>`<th>${text(k)}</th>`).join('')}</tr></thead><tbody>${codes.map(a=>`<tr><th scope="row">${text(a)}</th>${codes.map(b=>{
    if(a===b)return '<td class="self">·</td>';
    const verdict=edge(a,b)?.reason;
    return `<td class="${verdict==='COMPATIBLE'?'on':'off'}" title="${text(reason(verdict))}">${verdict==='COMPATIBLE'?'可叠':verdict==='EXCLUSIVE_GROUP'?'互斥':'未声明'}</td>`;
  }).join('')}</tr>`).join('')}</tbody></table></div>`;
}

export function optimizer(sale, qualification, picker) {
  if (!sale) return [head('小票明细',picker)+'<p>暂无已采信小票</p>',head('券对方阵')+'<p>等待小票</p>'];
  if(sale.status!=='solved') return [head('小票明细',picker)+pill(reason(sale.reason),'bad'),head('券对方阵')+rulesGrid(qualification)];
  return [head('小票明细',picker)+`<div id="selected-coupons" class="tags">${sale.chosen.map(c=>pill(c,'good')).join('')||pill('未用优惠券')}</div>`+
    grid(['行号','品类','件数','商品毛额','分摊','复算实付'],sale.lines.map(x=>[x.id,x.category,x.qty,cash(x.gross),cash(x.discount),cash(x.actual)]),[2,3,4,5])+
    `<div class="explain"><span>小票实付 ${cash(sale.paid)}</span><strong id="due">${cash(sale.due)}</strong></div><h3>入选券分摊</h3>`+
    grid(['券版本','明细分摊','减免'],sale.applied.map(x=>[`${x.code} · ${x.version}`,Object.entries(x.shares).map(([k,v])=>`${k} ${cash(v)}`).join(' / '),cash(x.amount)]),[2]),
    head('券对方阵',pill(`${sale.trial_count} 个合法组合`))+rulesGrid(qualification)+'<h3>金额最低的候选</h3>'+
    grid(['组合','复算实付'],sale.trials.slice(0,5).map(x=>[x.codes.join(' + ')||'原价',cash(x.due)]),[1])];
}
