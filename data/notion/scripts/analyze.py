import json,re,collections
BRANDS=['selene','salene','selena','selenepets','doggy spout','doggyspout','doggie spout','fresh flow','freshflow','rhykin','petlibro','pet libro','oneisall','feel needy','feelneedy','flowzy','pawspike','good origins','bissell','wagwells','vetiflow','coolistry','hydro paws','saker','potaroma','pure paw','vekonn','gugu','pawtrate','pawstream','pawquench','doggy fountain','doggie fountain','kitty spout','hapaw','catit','pixi','veken','elfin','pawria','pawira','uahpet','pokpet','dogness','petkit','orsda','apopo']
ATTR={'wireless':'无线','cordless':'无线','battery':'电池','rechargeable':'电池','stainless':'不锈钢','steel':'不锈钢','ceramic':'陶瓷','large':'大型/大容量','big':'大型/大容量','capacity':'大型/大容量','gallon':'大型/大容量','outdoor':'户外','inside':'室内','indoor':'室内','automatic':'自动','auto':'自动','filter':'过滤','filtered':'过滤','filterless':'无过滤','pumpless':'无泵','quiet':'静音','small':'小型','medium':'中型','motion':'感应','sensor':'感应','uv':'UV','smart':'智能','elevated':'抬高','electric':'电动','led':'LED','self':'自清洁','clean':'易清洁','plastic':'塑料','glass':'玻璃'}
def species(k):
    t=k.split()
    d=any(w in t for w in ['dog','dogs','doggy','doggie','puppy','perros','perro']) or 'dog' in k
    c=any(w in t for w in ['cat','cats','kitty','kitten','gatos','gato']) or 'cat ' in k+' '
    return 'dog+cat' if d and c else 'dog' if d else 'cat' if c else 'pet/通用'
def core(k):
    if 'fountain' in k: return 'water fountain/fountain'
    if 'bowl' in k: return 'water bowl'
    if 'dispenser' in k or 'waterer' in k: return 'water dispenser'
    if 'fuente' in k or 'bebedero' in k: return '西语'
    return '其他'
def parse(k):
    kl=k.lower()
    br=[b for b in BRANDS if b in kl]
    at=sorted({v for w,v in ATTR.items() if re.search(r'\b'+w+r'\b',kl)})
    lvl='品牌词' if br else ('一级' if not at else '二级' if len(at)==1 else '三级')
    return dict(brand=br,attrs=at,level=lvl,species=species(kl),core=core(kl))
out={}
for key,fname,th in [('dog','狗_准词表',4),('cat','猫_准词表',4)]:
    recs=json.load(open(fname+'__recs.json'))
    pool=[]
    for r in recs:
        if r['score'] is None or r['score']<th: continue
        p=parse(r['kw']); r.update(p)
        if key=='dog' and p['species'] not in ('dog','pet/通用','dog+cat'): continue
        if key=='cat' and p['species'] not in ('cat','pet/通用','dog+cat'): continue
        pool.append(r)
    pool.sort(key=lambda r:-r['sv'])
    out[key]=pool
    print('=====',key,len(pool),'sv',sum(r['sv'] for r in pool))
    print(collections.Counter((r['band'],r['level']) for r in pool))
    for lv in ['一级','二级','三级','品牌词']:
        L=[r for r in pool if r['level']==lv]
        print('--',lv,len(L),sum(r['sv'] for r in L))
        for r in L[:25]: print('   ',r['kw'],r['sv'],r['score'],r['species'],r['attrs'],r['brand'],'n',r['n_ranked'],'avg',r['avg_rank'],'own',r['own_rank'],'ad',r.get('ad_spend'),r.get('ad_orders'),r.get('ad_cpa'))
    ac=collections.Counter(); asv=collections.Counter()
    for r in pool:
        if r['level'] in('二级','三级'):
            for a in r['attrs']: ac[a]+=1; asv[a]+=r['sv']
    print('attrs',[(a,ac[a],asv[a]) for a,_ in asv.most_common()])
json.dump(out,open('pools.json','w'),ensure_ascii=False)
