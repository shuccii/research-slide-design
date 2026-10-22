"""6種類の追加レイアウト見本を生成する。全数値は架空の配置検証データ。"""
import os,sys,json
from pathlib import Path
import tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'research-slide-mpl'))
R=Path(__file__).resolve().parent.parent
O=R/'examples'/'out'/'layout_gallery'
O.mkdir(parents=True,exist_ok=True)
A=O/'assets';A.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'lib'))
from research_deck import Deck,COLORS,TYPO
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.style.use(str(R/'lib/research.mplstyle'))
plt.rcParams['savefig.bbox']=None
C=lambda k:COLORS[k]['value']
ink,accent,sub=C('ink'),C('accent'),C('ink-sub')
x=np.linspace(0,1,81);truth=np.sin(2*np.pi*x)
resA=.22*np.sin(4*np.pi*x)+.18*x
resB=.07*np.sin(4*np.pi*x)+.04*x
predA=truth+resA;predB=truth+resB
rmse=lambda a:float(np.sqrt(np.mean(a*a)))
font=TYPO['styles']['label']['size']
lw=json.loads((R/'tokens/charts.json').read_text())['line_width_pt']
def fig(name,w,h,draw):
 f,ax=plt.subplots(figsize=(w,h));f.subplots_adjust(left=.23 if w<5 else .14,right=.92,bottom=.24,top=.92)
 draw(ax);f.text(.99,.012,'見本データ',ha='right',va='bottom',fontsize=font,color=C('caption'));f.savefig(A/(name+'.png'),dpi=300);f.savefig(A/(name+'.pdf'));plt.close(f);return A/(name+'.png')
def curve(ax,pred,label):
 ax.plot(x,truth,color=sub,ls='--',lw=lw,label='真値')
 ax.plot(x,pred,color=accent if label=='構成B' else ink,lw=lw,marker='s' if label=='構成B' else 'o',markevery=10,label=label)
 ax.set(xlabel='入力 x [任意単位]',ylabel='応答 y [任意単位]',xlim=(0,1),ylim=(-1.3,1.3));ax.legend(loc='upper right',fontsize=font)
d=Deck('16:9');spec=[]
def slide(key,title,message,purpose,diff):
 s=d.slide(title,message);s.sources(['見本データ: 配置検証用の架空データ。研究結果ではない。デザイン見本。'])
 s.notes(f'レイアウト: {key}\n用途: {purpose}\n既存との差: {diff}\n数値はすべて配置検証用の架空データ。研究上の主張として使わない。')
 spec.append(dict(id=key,title=title,purpose=purpose,difference=diff));return s
# 01 paired comparison
s=slide('matched-comparison','同じ条件で比較すると、構成Bの誤差が小さい（見本）','01 対照比較: 左右の軸・条件・表の項目をそろえる','対照実験、前後比較、従来法と提案法の比較','two-figuresの派生。左右を対称にし、比較条件と対応する根拠を固定する。')
for c,p,label,res in [(0,predA,'構成A',resA),(6,predB,'構成B',resB)]:
 xx,w=s.col(c,6);s.heading(xx,1.12,w,label,size=18)
 path=fig('compare-'+label,w,3.15,lambda ax,p=p,l=label:curve(ax,p,l))
 s.image(path,xx,1.58,w,3.15)
 s.table(xx,4.84,w,[['共通の評価点数','RMSE [任意単位]'],['81',f'{rmse(res):.3f}']],size=14,row_h=.43)
 s.text(xx,5.95,w,.90,'入力範囲と真値を統一する。\n比較条件を左右で対応させる。' if c==0 else '見本では構成Bの誤差が小さい。\n複数の試行で再確認する。',size=20)
# 02 six small multiples
s=slide('small-multiples-6','6条件の変化を、共通軸で一度に比較する（見本）','02 条件一覧: 2段×3列。同じ軸とラベル位置を保つ','温度・試料・期間などの複数条件を一覧する','two-figuresの派生。3枚1列から6枚2段へ拡張し、短い条件名で統一する。')
for i in range(6):
 xx,w=s.col((i%3)*4,4);yy=1.1+(i//3)*2.55
 s.heading(xx,yy,w,f'({chr(97+i)}) 条件 {i+1}',size=16)
 def draw(ax,i=i):
  y=np.sin(2*np.pi*x)+(.05+i*.035)*np.cos(4*np.pi*x)
  ax.plot(x,truth,color=sub,ls='--');ax.plot(x,y,color=ink,marker='o',markevery=20)
  ax.set(xlim=(0,1),ylim=(-1.3,1.3),xlabel='x [任意単位]',ylabel='y [任意単位]');ax.set_xticks([0,.5,1]);ax.set_yticks([-1,0,1])
 p=fig(f'condition-{i+1}',w,2.16,draw);s.image(p,xx,yy+.32,w,2.16)
s.text(.4,6.30,s.width,.43,'比較条件を増やす場合も、軸範囲と系列の意味を全パネルでそろえる。',size=18)
# 03 overview zoom
s=slide('overview-detail','全体の傾向と局所のずれを、同じページで示す（見本）','03 全体と拡大: 左に全範囲、右に区間別の詳細を置く','ピーク、交点、外挿域など局所的な差を説明する','figure-notesの派生。右欄を説明文から拡大図2枚へ置換し、範囲を明記する。')
xx,w=s.col(0,8)
s.heading(xx,1.1,w,'(a) 全範囲',size=18)
p=fig('overview',w,4.30,lambda ax:curve(ax,predB,'構成B（全体）'));s.image(p,xx,1.5,w,4.30)
s.text(xx,5.97,w,.86,'全体図を比較の基準にする。\n拡大図には対象区間を明記する。',size=20)
xx,w=s.col(8,4)
for i,(lo,hi) in enumerate([(0.1,.3),(.65,.85)]):
 yy=1.1+i*2.84;s.heading(xx,yy,w,f'({chr(98+i)}) x = {lo:.2f}–{hi:.2f}',size=16)
 def detail(ax,lo=lo,hi=hi):
  ax.plot(x,truth,color=sub,ls='--');ax.plot(x,predB,color=accent,marker='s',markevery=3)
  m=(x>=lo)&(x<=hi);ax.set(xlim=(lo,hi),ylim=(min(truth[m].min(),predB[m].min())-.05,max(truth[m].max(),predB[m].max())+.05),xlabel='x [任意単位]',ylabel='y [任意単位]');ax.locator_params(nbins=3)
 p=fig(f'detail-{i}',w,2.35,detail);s.image(p,xx,yy+.33,w,2.35)
# 04 ablation
values=[.12,.19,.28];labels=['全要素あり','要素Pなし','要素Qなし']
s=slide('ablation','要素を一つずつ除き、誤差への寄与を確かめる（見本）','04 要素別検証: 変更した要素と固定条件を並べる','前処理、モデル要素、データ源の寄与を検証する','figure-tableの用途特化。結果の順位だけでなく、何を除いたかを対応表で示す。')
xx,w=s.col(0,7);s.heading(xx,1.12,w,'誤差の比較（小さいほどよい）',size=18)
def bars(ax):
 pos=np.arange(3);ax.barh(pos,values,color=[accent,ink,ink],height=.55)
 ax.set_yticks(pos,labels);ax.invert_yaxis();ax.set(xlabel='RMSE [任意単位]',xlim=(0,.34));ax.grid(axis='x',visible=False)
 for i,v in enumerate(values):ax.text(v+.008,i,f'{v:.2f}',va='center',fontsize=font,color=ink)
p=fig('ablation',w,3.6,bars)
# reserve room for the long y labels inside the plot
# regenerate with explicit left inset
f,ax=plt.subplots(figsize=(w,3.6));f.subplots_adjust(left=.27,right=.97,bottom=.22,top=.94);bars(ax);f.text(.99,.012,'見本データ',ha='right',va='bottom',fontsize=font,color=C('caption'));f.savefig(p,dpi=300);f.savefig(A/'ablation.pdf');plt.close(f)
s.image(p,xx,1.58,w,3.6)
s.text(xx,5.35,w,1.1,'要素Qを除いた見本で誤差が最大。\n寄与の一般化には、反復検証が必要。',size=20)
xx,w=s.col(7,5);s.heading(xx,1.12,w,'変えたもの・固定したもの',size=18)
s.table(xx,1.66,w,[['構成','P','Q'],['全要素あり','使用','使用'],['要素Pなし','除外','使用'],['要素Qなし','使用','除外']],size=14,row_h=.55)
s.heading(xx,4.14,w,'共通条件',size=18)
s.table(xx,4.66,w,[['項目','設定'],['評価点','同じ81点'],['指標','RMSE'],['試行','見本の単一値']],size=14,row_h=.48)
# 05 residual diagnosis
s=slide('error-diagnosis','誤差の平均値に加え、偏りと大きな残差を確認する（見本）','05 誤差の診断: 入力に対する残差、分布、代表点を対応させる','平均指標だけでは見えない系統誤差や外れ値を調べる','two-figuresとfigure-tableの組合せ。位置・分布・代表例の3種類の根拠を固定する。')
xx,w=s.col(0,7);s.heading(xx,1.10,w,'(a) 入力に対する残差',size=18)
def residual(ax):
 ax.axhline(0,color=sub,ls='--');ax.plot(x,resB,color=accent,marker='s',markevery=5)
 ax.set(xlabel='x [任意単位]',ylabel='予測値 − 真値 [任意単位]',ylim=(-.09,.12))
p=fig('residual',w,3.30,residual);s.image(p,xx,1.58,w,3.30)
s.text(xx,5.05,w,1.38,'残差は入力に応じて上下する。\n平均的な誤差が小さくても、\n系統的なずれは別に確認する。',size=20)
xx,w=s.col(7,5);s.heading(xx,1.10,w,'(b) 残差の分布',size=18)
def hist(ax):
 ax.hist(resB,bins=np.linspace(-.09,.12,10),color=ink,rwidth=.85)
 ax.set(xlabel='残差 [任意単位]',ylabel='度数 [点]',xlim=(-.09,.12));ax.locator_params(nbins=4)
p=fig('residual-hist',w,2.38,hist);s.image(p,xx,1.5,w,2.38)
s.heading(xx,4.10,w,'(c) 絶対残差が大きい代表点',size=16)
inds=np.argsort(np.abs(resB))[-3:][::-1]
s.table(xx,4.58,w,[['x [任意単位]','残差 [任意単位]']]+[[f'{x[i]:.3f}',f'{resB[i]:+.3f}'] for i in inds],size=14,row_h=.48)
# 06 evidence-next
s=slide('evidence-next','結論ごとに根拠と限界を結び、次の検証を決める（見本）','06 議論と次の検証: 1行に一つの結論と、その成立条件を置く','研究MTGの判断、考察、追加実験の相談に使う','summaryの派生。3段組の要約から、結論・根拠・限界・次の検証の対応表にする。')
s.heading(.4,1.12,s.width,'見本データから読めることと、追加で確かめること',size=18)
s.table(.4,1.68,s.width,[['結論','対応する根拠','限界','次の検証'],['構成Bの誤差が小さい',f'RMSE {rmse(resB):.3f}\n構成A {rmse(resA):.3f}','単一の合成関数','異なる関数で反復'],['要素Qの除外で誤差増','要素別検証の\n見本値 0.28','要素間の相互作用は未評価','PとQを同時に除外'],['残差が入力で変化','残差図の\n周期的な変動','測定ノイズを含まない','ノイズ条件を追加']],col_widths=[s.col(0,3)[1]+s.gutter,s.col(3,3)[1]+s.gutter,s.col(6,3)[1]+s.gutter,s.col(9,3)[1]],size=16,row_h=.86)
s.heading(.4,5.42,s.width,'今回の相談事項',size=18)
s.text(.4,5.92,s.width,.88,'次の検証を一つ選び、必要なデータと判断基準を決める。',size=22)
d.save(O/'layout_gallery_16x9.pptx',title='研究スライドの追加レイアウト6種（見本）')
(O/'layout-manifest.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))

(O/'sample-data.json').write_text(json.dumps({'x':x.tolist(),'truth':truth.tolist(),'prediction_a':predA.tolist(),'prediction_b':predB.tolist(),'ablation':dict(zip(labels,values))},ensure_ascii=False,indent=2))
np.savez(A/'sample-data.npz',x=x,truth=truth,predA=predA,predB=predB,resA=resA,resB=resB)
print(O);print('6 slides; sample RMSE A',rmse(resA),'B',rmse(resB))
