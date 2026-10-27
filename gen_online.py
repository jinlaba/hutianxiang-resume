#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在线简历页生成器（双版本切换：财务BP / 财务经理）

数据源：工作区 resume_engine/jobs_cat.py 的 FIN_BP / FIN_MGR / HIGHLIGHTS_CAT
——与 PDF 版共用同一份配置，改一处三处同步。

用法：python3 gen_online.py
输出：index.html（同目录）
"""
import pathlib
import sys

WS = "/home/hu/WorkBuddy/2026-09-10-19-07-12"
sys.path.insert(0, WS + "/resume_engine")
sys.path.insert(0, "/home/hu/WorkBuddy/2026-10-19-16-58-42/resume_engine")

from jobs_cat import FIN_BP, FIN_MGR, HIGHLIGHTS_CAT  # noqa: E402

OUT = pathlib.Path(__file__).resolve().with_name("index.html")
TODAY = "2026-10"

# 公开页面的 note 改写：内部口径不上外网
NOTE_MAP = {
    "工作语言：法语（仅阅读）": "盛世阳光任职期间参与，项目以国内远程支持为主",
}

EDU = ("周口师范学院", "财务管理 · 本科（全日制）", "2010 - 2014", "学士学位")
CERTS = [
    ("中级会计师", "2020"),
    ("CMA 美国注册管理会计师", "2022"),
    ("CPA 注册会计师", "专业阶段已过 4 科：会计 / 战略 / 财管 / 税法"),
]

WORKS = [
    ("食品电商盈利分析看板", "9 个平台 / 812 个商品 / 6.3 万行 SKU-日 明细",
     "单品盈亏平衡、推广 ROI 预警、低毛利品类拆解、分平台利润贡献",
     "https://jinlaba.github.io/Baotao-Profit-Demo/"),
    ("房产租赁经营分析看板", "7381+ 条房源 / 16 类房源明细",
     "房源结构透视、租金与空置率关联、分小区分类型经营指标，可下钻单套",
     "https://jinlaba.github.io/dingding-house-demo/"),
]

CSS = """
:root{--ink:#1f2733;--navy:#16294a;--navy2:#1f3a66;--accent:#c8a25a;
--soft:#f3ead6;--line:#e6e9ef;--muted:#5b6675;--bg:#eef1f6;--card:#fff}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
background:var(--bg);color:var(--ink);line-height:1.72;font-size:16px;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:28px auto;padding:0 16px}
.hero{background:linear-gradient(135deg,var(--navy),var(--navy2));color:#fff;border-radius:18px 18px 0 0;
padding:40px 40px 26px;position:relative;overflow:hidden}
.hero::after{content:'';position:absolute;right:-50px;top:-50px;width:200px;height:200px;
background:radial-gradient(circle,rgba(200,162,90,.28),transparent 70%)}
.hero h1{font-size:38px;font-weight:800;letter-spacing:3px;position:relative;z-index:1}
.hero .pos{font-size:16px;color:var(--accent);font-weight:600;letter-spacing:.5px;margin-top:6px;position:relative;z-index:1}
.hero .meta{margin-top:14px;font-size:14px;opacity:.9;display:flex;gap:20px;flex-wrap:wrap;position:relative;z-index:1}
.hero .meta a{color:#fff;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.35)}
.tabs{display:flex;background:#101f3a;position:relative;z-index:2}
.tab{flex:1;text-align:center;padding:14px 8px;color:#9fb0c8;font-size:15.5px;font-weight:700;
cursor:pointer;letter-spacing:1px;border-bottom:3px solid transparent;transition:.18s;-webkit-tap-highlight-color:transparent}
.tab.on{color:#fff;background:var(--navy2);border-bottom-color:var(--accent)}
.tab span{display:block;font-size:11.5px;font-weight:400;opacity:.6;letter-spacing:0;margin-top:2px}
.main{background:var(--card);border-radius:0 0 18px 18px;padding:38px 40px 44px;box-shadow:0 10px 40px rgba(20,30,50,.08)}
.panel{display:none}.panel.on{display:block}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:26px}
.card{border:1px solid var(--line);border-top:3px solid var(--accent);border-radius:10px;padding:14px 12px;text-align:center;background:#fcfcfd}
.card b{display:block;font-size:22px;color:var(--navy);letter-spacing:.5px}
.card i{display:block;font-size:12px;color:var(--muted);font-style:normal;margin-top:4px;line-height:1.4}
h2{font-size:20px;font-weight:800;color:var(--navy);border-left:5px solid var(--accent);
padding-left:12px;margin:30px 0 14px;letter-spacing:.5px}
h2:first-of-type{margin-top:0}
.job{padding:14px 0;border-bottom:1px dashed var(--line)}
.job:last-child{border-bottom:none}
.job .top{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}
.job .co{font-size:16.5px;font-weight:700;color:var(--navy)}
.job .role{font-size:14px;color:var(--accent);font-weight:700;margin-left:8px}
.job .when{font-size:13px;color:var(--muted);white-space:nowrap}
.job .note{font-size:12.5px;color:var(--muted);margin-top:3px}
ul{list-style:none;margin-top:8px}
li{position:relative;padding-left:18px;margin-bottom:7px;font-size:15px;color:#374151}
li::before{content:'';position:absolute;left:3px;top:10px;width:6px;height:6px;border-radius:50%;background:var(--accent)}
.num{color:var(--navy);font-weight:800}
strong{color:var(--navy);font-weight:700}
.skill{display:grid;grid-template-columns:96px 1fr;gap:10px;padding:9px 0;border-bottom:1px solid #f1f3f7;font-size:14.5px}
.skill b{color:var(--navy);font-size:14px}
.skill:last-child{border-bottom:none}
.edu{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;font-size:15px;padding:6px 0}
.edu b{color:var(--navy)}
.certs{margin-top:8px}
.wk{display:grid;gap:12px}
.wkitem{border:1px solid var(--line);border-radius:10px;padding:14px 16px;background:#fcfcfd}
.wkitem b{color:var(--navy);font-size:15px}
.wkitem p{font-size:13.5px;color:var(--muted);margin-top:4px}
.wkitem a{font-size:13px;color:var(--navy2);word-break:break-all}
.foot{text-align:center;padding:20px;font-size:12.5px;color:#9aa3b2}
@media(max-width:640px){
 .wrap{margin:0;padding:0}.hero{border-radius:0;padding:28px 20px 22px}.hero h1{font-size:30px}
 .main{padding:24px 18px 30px;border-radius:0}.cards{grid-template-columns:repeat(2,1fr);gap:8px}
 .card b{font-size:19px}.tab{font-size:14px}
}
@media print{body{background:#fff}.wrap{margin:0;max-width:100%}.main,.hero{box-shadow:none}
 .tabs{display:none}.panel{display:block!important}.panel+.panel{page-break-before:always}}
"""

JS = """
function go(id,el){
  document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('on')});
  document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('on')});
  document.getElementById(id).classList.add('on');el.classList.add('on');
  try{history.replaceState(null,'','#'+id)}catch(e){}
}
window.addEventListener('load',function(){
  var h=location.hash.replace('#','');
  if(h==='mgr'){var t=document.querySelectorAll('.tab')[1];go('mgr',t)}
});
"""


def sec_adv(cfg):
    return "".join(f"<li><strong>{t}</strong>：{d}</li>" for t, d in cfg["adv"])


def sec_exp(cfg):
    out = []
    for when, co, role, note, bullets in cfg["exp"]:
        note = NOTE_MAP.get(note, note)
        n = f"<div class='note'>{note}</div>" if note else ""
        bl = "".join(f"<li>{b}</li>" for b in bullets)
        out.append(
            f"<div class='job'><div class='top'><div><span class='co'>{co}</span>"
            f"<span class='role'>{role}</span></div><div class='when'>{when}</div></div>"
            f"{n}<ul>{bl}</ul></div>"
        )
    return "".join(out)


def sec_proj(cfg):
    out = []
    for when, co, role, note, bullets in cfg["proj"]:
        note = NOTE_MAP.get(note, note)
        n = f"<div class='note'>{note}</div>" if note else ""
        bl = "".join(f"<li>{b}</li>" for b in bullets)
        out.append(
            f"<div class='job'><div class='top'><div><span class='co'>{co}</span>"
            f"<span class='role'>{role}</span></div><div class='when'>{when}</div></div>"
            f"{n}<ul>{bl}</ul></div>"
        )
    return "".join(out)


def sec_cards(cfg):
    hs = HIGHLIGHTS_CAT.get(cfg["file"], [])
    items = "".join(f"<div class='card'><b>{n}</b><i>{d}</i></div>" for n, d in hs)
    return f"<div class='cards'>{items}</div>"


def sec_skill(cfg):
    return "".join(f"<div class='skill'><b>{k}</b><div>{v}</div></div>" for k, v in cfg["skills"])


def sec_work():
    items = "".join(
        f"<div class='wkitem'><b>{t}</b><p>{d}｜{c}</p><a href='{u}' target='_blank'>{u}</a></div>"
        for t, d, c, u in WORKS
    )
    return f"<div class='wk'>{items}</div>"


def edu_block():
    sch, major, years, deg = EDU
    certs = "".join(f"<li><strong>{a}</strong>（{b}）</li>" if b and len(b) < 20
                    else f"<li><strong>{a}</strong>：{b}</li>" for a, b in CERTS)
    return (f"<div class='edu'><div><b>{sch}</b> ｜ {major} ｜ {deg}</div>"
            f"<div class='when'>{years}</div></div><ul>{certs}</ul>")


def panel(pid, cfg, on):
    return f"""
<div class='panel{on}' id='{pid}'>
  {sec_cards(cfg)}
  <h2>个人优势</h2>
  <ul>{sec_adv(cfg)}</ul>
  <h2>工作经历</h2>
  {sec_exp(cfg)}
  <h2>项目经历</h2>
  {sec_proj(cfg)}
  <h2>教育背景与资质</h2>
  {edu_block()}
  <h2>专业技能</h2>
  {sec_skill(cfg)}
  <h2>数据作品（在线可交互）</h2>
  {sec_work()}
</div>"""


def build():
    return f"""<!DOCTYPE html>
<html lang='zh-CN'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1.0'>
<title>胡天祥 · 财务BP／财务经理 · 在线简历</title>
<meta name='description' content='胡天祥，12 年财务全盘管理，财务BP／财务经理。经营分析、盈利模型、预算管控、合并报表，SQL/Python/Power BI。'>
<style>{CSS}</style>
</head>
<body>
<div class='wrap'>
  <div class='hero'>
    <h1>胡天祥</h1>
    <div class='pos'>财务BP ／ 财务经理 ｜ 长沙 ｜ 12 年财务全盘管理</div>
    <div class='meta'>
      <span>📱 15674857125</span>
      <span>✉️ 894102027@qq.com</span>
      <span>📍 长沙 · 岳麓区</span>
    </div>
    <div class='meta'><span>面试可现场打开下方数据作品，均为本人实操搭建</span></div>
  </div>
  <div class='tabs'>
    <div class='tab on' onclick="go('bp',this)">财务 BP 版<span>经营分析 · 盈利模型 · 业财协同</span></div>
    <div class='tab' onclick="go('mgr',this)">财务经理版<span>全盘账务 · 预算 · 团队</span></div>
  </div>
  <div class='main'>
    {panel('bp', FIN_BP, ' on')}
    {panel('mgr', FIN_MGR, '')}
  </div>
  <div class='foot'>更新于 {TODAY} ｜ 简历内容与本人实际经历一致，可提供任一段的凭证与报表样例（脱敏）</div>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main():
    OUT.write_text(build(), encoding="utf-8")
    print(f"[√] 已生成 {OUT}  ({OUT.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
