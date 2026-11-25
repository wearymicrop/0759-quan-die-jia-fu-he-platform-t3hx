export const el = selector => document.querySelector(selector);
export const text = value => String(value ?? '—').replace(/[&<>"']/g, token=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[token]));
export const cash = value => value == null ? '—' : '¥'+(value/100).toLocaleString('zh-CN',{minimumFractionDigits:2,maximumFractionDigits:2});
const labels={ACCEPTED:'采信',BAD_JSON:'流水截断',BAD_EVENT:'字段异常',EMPTY_ROW:'空行',DUPLICATE_REPLAY:'重复回传',DUPLICATE_CONFLICT:'同键冲突',VERSION_OVERLAP:'版本重叠',QUALIFIED:'符合资格',RULE_UNKNOWN:'无此券',RULE_INACTIVE:'券已失效',MINIMUM_NOT_MET:'未达门槛',SHOP_MISMATCH:'门店不符',CATEGORY_MISMATCH:'商品不符',COMPATIBLE:'准许叠用',EXCLUSIVE_GROUP:'同组互斥',PAIR_UNDECLARED:'缺兼容声明',SALE_MISSING:'原单缺失',SALE_ISOLATED:'原单隔离',SALE_LINE_MISSING:'原明细缺失',RETURN_BEFORE_SALE:'早于原购',RETURN_OVER_QTY:'超出可退件数',SALE_CASH_GAP:'销售实付差异',RETURN_CASH_GAP:'退款实付差异',LINE_IMBALANCE:'逐行未对平'};
export const reason = code => labels[code] || code || '—';
export const head = (title, extra='') => `<div class="panel-header"><h2>${text(title)}</h2>${extra}</div>`;
export const pill = (label, theme='') => `<span class="pill ${theme}">${text(label)}</span>`;
export function grid(headers, records, numeric=[]) {
  if (!records.length) return '<p>暂无对应记录</p>';
  return `<div class="scroll" tabindex="0"><table><thead><tr>${headers.map(label=>`<th>${text(label)}</th>`).join('')}</tr></thead><tbody>${records.map(record=>`<tr>${record.map((field,i)=>`<td${numeric.includes(i)?' class="number"':''}>${text(field)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
