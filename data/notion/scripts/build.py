import openpyxl,csv,json,re,statistics,collections,warnings
warnings.filterwarnings('ignore')
B='/workspace/ads-kb/notion/'
SRC={'page':'词库','url':'https://app.notion.com/p/401ac7523016817d9581d73a9cd97ea1','archived':'2026-10-22'}
def num(x):
    try: return float(x)
    except: return None
def tier(sv):
    if sv is None or sv<1000: return 'L0(<1,000 总纲未定义)'
    for lo,hi,n in [(1000,3000,'L1'),(3000,6000,'L2'),(6000,10000,'L3'),(10000,50000,'L4'),(50000,100000,'L5'),(100000,200000,'L6'),(200000,300000,'L7')]:
        if lo<=sv<hi: return n
    return 'L8'
def band(s):
    if s is None: return '无分数(-)'
    if s>=8: return '8–10'
    if s>=6: return '6–<8'
    if s>=4: return '4–<6'
    return '<4'
def dump(ws,name):
    rows=[list(r) for r in ws.iter_rows(values_only=True)]
    while rows and all(v is None for v in rows[-1]): rows.pop()
    with open(B+name+'.csv','w',newline='',encoding='utf-8-sig') as f: csv.writer(f).writerows(rows)
    return rows
def md_table(h,rows):
    esc=lambda v:'' if v is None else str(v).replace('|','\\|').replace('\n',' ')
    out=['| '+' | '.join(esc(x) for x in h)+' |','|'+'---|'*len(h)]
    out+=['| '+' | '.join(esc(x) for x in r)+' |' for r in rows]
    return '\n'.join(out)
res={}
for key,f,main,title,fname in [('cat','raw/cat.xlsx','准词表原始','猫喂水器准词表.xlsx','猫_准词表'),('dog','raw/all.xlsx','Table','喂水器全词表终.xlsx','狗_准词表')]:
    wb=openpyxl.load_workbook(B+f,read_only=True,data_only=True)
    sheets={}
    for ws in wb.worksheets:
        rows=dump(ws, fname if ws.title==main else f'{fname}__{ws.title}')
        sheets[ws.title]=len(rows)-1
    rows=[list(r) for r in wb[main].iter_rows(values_only=True)]
    h=rows[0]; d=[r for r in rows[1:] if r[0] is not None]
    comp=[c for c in h if str(c).startswith('B0')]
    ci=[h.index(c) for c in comp]
    def ranks(r): return [int(r[i]) for i in ci if num(r[i]) not in (None,0)]
    recs=[]
    for r in d:
        s=num(r[6]); sv=r[2] or 0; rk=ranks(r)
        rec=dict(kw=str(r[0]),sales=r[1],sv=sv,share=r[3],cpr=r[4],own_rank=r[5],score=s,band=band(s),tier=tier(sv),
                 n_ranked=len(rk),avg_rank=round(statistics.mean(rk),1) if rk else None,var=round(statistics.pvariance(rk),1) if len(rk)>1 else None,
                 in_share_subset=r[3] is not None)
        if key=='dog': rec.update(ad_spend=num(r[13]),ad_orders=num(r[14]),ad_cpa=num(r[15]),ad_cvr=num(r[16]),ad_cpc=num(r[17]),ad_acos=num(r[18]))
        else: rec.update(ad_clicks=num(r[13]),ad_orders=num(r[18]),ad_cpa=num(r[16]),ad_acos=num(r[15]))
        recs.append(rec)
    # enriched csv
    with open(B+fname+'__分析字段.csv','w',newline='',encoding='utf-8-sig') as fo:
        w=csv.DictWriter(fo,fieldnames=list(recs[0].keys())); w.writeheader(); w.writerows(recs)
    bc=collections.Counter(x['band'] for x in recs); bsv=collections.Counter()
    for x in recs: bsv[x['band']]+=x['sv']
    res[key]=dict(title=title,sheet=main,sheets=sheets,rows=len(d),cols=list(h),competitors=comp,band_count=dict(bc),band_sv=dict(bsv),
        share_subset=sum(x['in_share_subset'] for x in recs),share_subset_sv=sum(x['sv'] for x in recs if x['in_share_subset']),
        tier_count=dict(collections.Counter(x['tier'] for x in recs)),
        top_sv=[(x['kw'],x['sv'],x['score']) for x in sorted(recs,key=lambda x:-x['sv'])[:15]])
    # markdown
    mdh=['关键词词组','搜索量','竞品表现得分','分数段','总纲搜索量层级','有排名竞品数','竞品平均自然排名','自身自然排名']+(['在搜索占比子集(≥6分准词池)','历史广告花费','历史广告订单','历史CPA'] if key=='dog' else ['历史广告点击','历史广告订单'])
    mdrows=[[x['kw'],x['sv'],x['score'],x['band'],x['tier'],x['n_ranked'],x['avg_rank'],x['own_rank']]+([('是' if x['in_share_subset'] else ''),x['ad_spend'],x['ad_orders'],x['ad_cpa']] if key=='dog' else [x['ad_clicks'],x['ad_orders']]) for x in recs]
    with open(B+fname+'.md','w',encoding='utf-8') as fo:
        fo.write(f"# {fname}（从 Notion 同步，只读）\n\n- 来源页面：Notion「{SRC['page']}」 {SRC['url']} （页面归档日期 {SRC['archived']}）\n- 来源附件：{title}；主表 sheet：{main}\n- 同步时间：2026-11-14（Asia/Shanghai）\n- 主表行数：{len(d)}；列：{', '.join(map(str,h))}\n- 其他 sheet（已另存 CSV）：{json.dumps(sheets,ensure_ascii=False)}\n- 分数段/搜索量层级/竞品平均排名为本次按总纲 2.3、3.2、五 计算的辅助字段，不是表内原有分类；准词阈值按口径是变量。\n\n"+md_table(mdh,mdrows)+"\n")
    json.dump(recs,open(B+fname+'__recs.json','w'),ensure_ascii=False)
json.dump(res,open(B+'summary.json','w'),ensure_ascii=False,indent=1)
print(json.dumps(res,ensure_ascii=False,indent=1))
