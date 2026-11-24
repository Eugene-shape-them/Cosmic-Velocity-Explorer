'''
宇宙速度探究器 · 课堂学生版

'''

import ctypes
import sys
import time
from collections import deque
from pathlib import Path
import numpy as np
import matplotlib
HEADLESS = '--headless' in sys.argv
matplotlib.use('Agg' if HEADLESS else 'TkAgg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.animation import FuncAnimation
from matplotlib.patches import (Circle, FancyArrowPatch, FancyBboxPatch, Rectangle)
from matplotlib.transforms import Bbox
from matplotlib.widgets import (Button, CheckButtons, Slider, TextBox)
_available = {f.name for f in font_manager.fontManager.ttflist}
CN_FONTS = [name for name in ('Microsoft YaHei', 'SimHei', 'DengXian', 'Noto Sans CJK SC', 'WenQuanYi Zen Hei') if name in _available]
plt.rcParams['font.sans-serif'] = CN_FONTS + ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
UI_LANG = 'zh'
_LANG_ARTISTS = []

def T(s):
    '''界面文案翻译：中文模式原样返回；英文模式查词表，查不到就显示原文。'''

    if UI_LANG == 'zh':
        return s
    return _EN.get(s, s)

def _reg_text(artist, zh):
    '''创建静态文本时登记：按当前语言写入，切换语言时能一键换掉。'''

    artist.set_text(T(zh))
    _LANG_ARTISTS.append((artist, zh))
    return artist

_EN = {'近地圆轨道': 'Near-Earth Circular Orbit', '地球同步轨道': 'Geostationary Orbit', '地月转移轨道': 'Earth-Moon Transfer', '脱离地球': 'Earth Escape', '飞出太阳系': 'Leave the Solar System', '变轨与降轨': 'Orbit Raise & Lower', '环绕': 'Orbit', '同步': 'Geo', '奔月': 'Moon', '离地': 'Escape', '出系': 'Solar', '变轨': 'Hohmann', '把椭圆轨道修圆：让它稳定绕地球飞行，不再忽高忽低。': 'Circularize the ellipse: fly steadily around Earth, no more wobbling.', '分两步升到同步轨道：先抬高远地点，再在远地点把椭圆修圆。': 'Two steps to GEO: raise the apogee first, then circularize there.', '先转移去月球，再近月制动被捕获，最后修成环月圆轨道。': 'Transfer to the Moon, brake to get captured, then circularize into a lunar orbit.', '把速度加到逃逸速度以上，让飞船不再被地球拉回来。': 'Push speed above escape velocity so Earth can no longer pull the craft back.', '把速度加到第三宇宙速度以上，飞出太阳系。': 'Exceed the third cosmic velocity and leave the Solar System.', '先升到 1200 km 圆轨道，再降回 300 km 圆轨道：加速升轨、减速降轨，每次都要再点火修圆。': 'Rise to a 1200 km circular orbit, then lower back to 300 km: burn to raise, burn to lower, and circularize after every burn.', '修圆': 'Circularize', '抬远地点': 'Raise apogee', '远地点修圆': 'Circularize at apogee', '地月转移': 'Trans-lunar cruise', '近月制动': 'Lunar braking', '环月修圆': 'Lunar circularize', '逃逸': 'Escape', '加速升轨': 'Burn: raise', '减速降轨': 'Burn: lower', '近地点修圆': 'Circularize at perigee', '环月圆轨道': 'Circular lunar orbit', '环月椭圆轨道': 'Elliptic lunar orbit', '圆轨道': 'Circular orbit', '椭圆轨道': 'Elliptic orbit', '地球': 'Earth', '月球': 'Moon', '月球公转轨道': "Moon's orbit around Earth", '近地轨道': 'Low Earth orbit', '同步轨道': 'Synchronous orbit', '近地点': 'Perigee', '远地点': 'Apogee', '宇宙速度探究器': 'Cosmic Velocity Explorer', '拖速度滑块 → 看虚线 → 点火': 'Drag slider → preview → fire', '沉浸 V': 'Immersive V', '沉浸 √': 'Immersive √', '受力分析 F': 'Forces F', '暂停': 'Pause', '继续': 'Resume', '已暂停': 'Paused', '重新发射': 'Relaunch', '① 任务与操作': '① Task & controls', '② 原理与案例': '② Theory & missions', '达成条件': 'Goals', '操作提示': 'Guidance', '实时飞行数据': 'Live data', '合理速度范围（当前位置）': 'Reasonable speed range (at current position)', '现实中的航天任务': 'Real-world missions', '建议点火点：{a}': 'Burn point: {a}', '推荐速度 ≈ {a:.2f} km/s{b}': 'Recommended ≈ {a:.2f} km/s{b}', '（相对月球）': ' (rel. Moon)', '为什么：{a}  → 看「② 原理与案例」': 'Why: {a}  → see ② Theory & missions', '任务 {a} / {b}{c}': 'Task {a} / {b}{c}', ' · 第 {a}/{b} 步：{c}': ' · step {a}/{b}: {c}', '速度 {a:.2f}   高度 {b:,.0f} km': 'Speed {a:.2f}   altitude {b:,.0f} km', '近地点 {a:,.0f}   远地点 {b:,.0f} km': 'Perigee {a:,.0f}   apogee {b:,.0f} km', '近地点 {a:,.0f} km   远地点 ∞': 'Perigee {a:,.0f} km   apogee ∞', '偏心率 e = {a:.3f}   机械能 ε = {b:.2f}': 'Eccentricity e = {a:.3f}   energy ε = {b:.2f}', '任务 {a} / {b}{c} · {d}：为什么用这个速度？': 'Task {a} / {b}{c} · {d}: why this speed?', '≥ {a:.2f} km/s（越快越好）': '≥ {a:.2f} km/s (faster is better)', '推荐 {a:.2f} km/s{b}。{c}': 'Recommended {a:.2f} km/s{b}. {c}', '当前速度 {a}': 'Current speed: {a}', '现在还没点火，先用滑块预览虚线': 'Not launched yet — preview the dashed line with the slider', '拓展知识：{a}': 'Did you know: {a}', '相对月球 {a:.2f} km/s   距月面 {b:,.0f} km\n当前轨道：{c}（近月点 {d:,.0f} km，e = {e:.2f}）{f}': 'Rel. Moon {a:.2f} km/s   above lunar surface {b:,.0f} km\nCurrent orbit: {c} (perilune {d:,.0f} km, e = {e:.2f}){f}', '速度 {a:.2f} km/s   高度 {b:,.0f} km\n当前轨道：{c}{f}': 'Speed {a:.2f} km/s   altitude {b:,.0f} km\nCurrent orbit: {c}{f}', '地球引力': "Earth's pull", '月球引力': "Moon's pull", '切向': 'Tangential', '法向': 'Normal', '受力分析 · 飞船（按 F 关闭）': 'Force analysis · spacecraft (F to close)', '地球引力 {a} m/s²   指向地心': "Earth gravity {a} m/s²   toward Earth's center", '月球引力 {a} m/s²   指向月心': "Moon gravity {a} m/s²   toward Moon's center", '合力 {a} m/s²   （地球占 {b:.1f}%）': 'Net force {a} m/s²   (Earth share {b:.1f}%)', '切向分量 {a:+.3f} m/s²   {b}': 'Tangential {a:+.3f} m/s²   {b}', '速率在变大': 'speeding up', '速率在变小': 'slowing down', '速率不变': 'speed constant', '法向分量 {a} m/s²   负责让轨道拐弯': 'Normal {a} m/s²   bends the orbit', '绕{a}圆轨道需要 v²/r = {b} m/s²': 'v²/r for a circular orbit around {a} = {b} m/s²', '引力 {a} {b} {c} → {d}': 'Gravity {a} {b} {c} → {d}', '高度：{a}（径向速度 {b:+.2f} km/s）': 'Altitude: {a} (radial speed {b:+.2f} km/s)', '正在升高': 'rising', '正在降低': 'falling', '基本不变': 'steady', '向心力过剩，轨道向{a}一侧弯': 'Centripetal surplus - orbit bends toward the {a}', '引力拉不住，轨道被甩向外侧': "Gravity can't hold it - orbit flung outward", '引力刚好等于需要的向心力 —— 这就是圆轨道': 'Gravity exactly equals the required centripetal force - a circular orbit', '（相对月球）{a:.2f} km/s → {b}｜近月点 {c:,.0f} km｜远月点 {d:,.0f} km｜e = {e:.3f}｜{f}': '(rel. Moon) {a:.2f} km/s → {b} | perilune {c:,.0f} km | apolune {d:,.0f} km | e = {e:.3f} | {f}', '×（相对月球）{a:.2f} km/s 仍超过逃逸速度 {b:.2f} km/s —— 抓不住，会飞掠而过｜{c}': '× (rel. Moon) {a:.2f} km/s still exceeds escape speed {b:.2f} km/s - no capture, it will fly past | {c}', '若以 {a:.2f} km/s 点火 → {b}｜e = {c:.3f}｜远地点 {d}｜{e}': 'If fired at {a:.2f} km/s → {b} | e = {c:.3f} | apogee {d} | {e}', '× {a:.2f} km/s 太慢了！这条预览线会撞进地球，速度要升到虚线参考值附近才飞得起来': '× {a:.2f} km/s is too slow! This preview path would crash into Earth - raise the speed toward the reference lines', '拖动滑块：亮青色虚线就是「如果现在点火」的轨道': 'Drag the slider: the cyan dashed line is the orbit if you fire now', '点 火（按 Enter）': 'FIRE (Enter)', '√ 已超过第三宇宙速度，连太阳也拉不住': "√ Beyond the third cosmic velocity - even the Sun can't hold it", '还差 {a:.2f} km/s 才够 16.7': '{a:.2f} km/s short of 16.7', '偏慢 {a:.2f} km/s': 'too slow by {a:.2f} km/s', '偏快 {a:.2f} km/s': 'too fast by {a:.2f} km/s', '√ 落在合理速度区间': '√ Within the reasonable range', '轨道是圆（偏心率 < 0.05）': 'Orbit is circular (e < 0.05)', '近地点高度在 150~1500 km': 'Perigee altitude 150-1500 km', '第 1 步：远地点升到同步轨道附近': 'Step 1: raise apogee near GEO radius', '第 2 步：在远地点把椭圆修圆（e < 0.05）': 'Step 2: circularize at apogee (e < 0.05)', '半长轴落在同步轨道 ±3%': 'Semi-major axis within ±3% of GEO', '转移：远地点到月球轨道 ±20%': "Transfer: apogee within ±20% of the Moon's orbit", '近月制动：被月球捕获（相对月球 ε<0）': 'Lunar braking: captured (rel. Moon ε<0)', '不撞月：近月点高度 > 100 km': 'No impact: perilune altitude > 100 km', '修成环月圆轨道（相对月球 e < 0.15）': 'Circular lunar orbit (rel. Moon e < 0.15)', '① 升轨：远地点抬到 1200 km': '① Raise: apogee up to 1200 km', '② 修圆：1200 km 圆轨道（e<0.05）': '② Circularize: 1200 km circular (e<0.05)', '③ 降轨：近地点降到 300 km': '③ Lower: perigee down to 300 km', '④ 修圆：300 km 圆轨道（e<0.05）': '④ Circularize: 300 km circular (e<0.05)', '机械能 ≥ 0（不再被地球束缚）': 'Mechanical energy ≥ 0 (no longer bound)', '速度超过逃逸速度': 'Speed above escape velocity', '速度 ≥ 16.7 km/s': 'Speed ≥ 16.7 km/s', '已经脱离地球引力': "Already free of Earth's gravity", '远地点 {a:,.0f} km（目标约 {b:,.0f}）': 'apogee {a:,.0f} km (target ≈ {b:,.0f})', '远地点 {a:,.0f} km，差 {b:,.0f} km': 'apogee {a:,.0f} km, off by {b:,.0f} km', '相对月球 {a:.2f} / 逃逸 {b:.2f} km/s': 'rel. Moon {a:.2f} / escape {b:.2f} km/s', '近月点 {a:,.0f} km': 'perilune {a:,.0f} km', '还没被捕获': 'not captured yet', '√ 已完成': '√ done', '近地点 {a:,.0f} km': 'perigee {a:,.0f} km', '飞掠近月点（刹车被捕获）': 'Close lunar flyby (brake to be captured)', '环月远月点（减速压低近月点）': 'Lunar apolune (brake to lower perilune)', '环月近月点（减速修圆）': 'Lunar perilune (brake to circularize)', '当前位置（近地点，加速升轨）': 'Current position (perigee, burn to raise)', '转移轨道远地点（补速修圆）': 'Transfer apogee (add speed to circularize)', '当前位置（高轨，减速降轨）': 'Current position (high orbit, brake to lower)', '转移轨道近地点（减速修圆）': 'Transfer perigee (brake to circularize)', '转移轨道远地点': 'Transfer apogee', '当前位置（近地点）': 'Current position (perigee)', '近地点（向外加速）': 'Perigee (accelerate outward)', '近地点（朝月球方向出发）': 'Perigee (head toward the Moon)', '近地点（脱离地球）': 'Perigee (escape Earth)', '近地点（继续加速）': 'Perigee (keep accelerating)', '当前位置': 'Current position', '这里相对月球跑得最快，反向点火减速最省燃料；减到推荐值就会被月球抓住。': 'Relative to the Moon this is the fastest point - braking here saves the most fuel; slow to the recommended value and the Moon captures you.', '在远月点减速，对面那个近月点就会被压低；先把它压到 500 km 高度。': 'Brake at apolune and the perilune opposite gets pushed down; first bring it to 500 km altitude.', '近月点速度最大，削到这里圆轨道需要的速度，远月点就被拉下来 —— 椭圆变圆。': 'Perilune is fastest; trim to the circular speed here and the apolune drops - the ellipse becomes a circle.', '在近地点加速：这一端不动，对面的远地点被抬到 1200 km。': 'Accelerate at perigee: this end stays put, the apogee opposite rises to 1200 km.', '远地点跑得最慢，补到这里的圆轨道速度就能把椭圆撑圆。': 'Apogee is the slowest point; add the circular speed here and the ellipse swells into a circle.', '在高轨道反向点火：这一端变远地点，对面的近地点被压到 300 km。': 'Retro-burn in the high orbit: this end becomes apogee and the perigee opposite drops to 300 km.', '近地点跑得最快，削到这里的圆轨道速度就能把椭圆修圆。': 'Perigee is the fastest point; trim to the circular speed here and the ellipse becomes a circle.', '远地点速度最慢，这里补一点速度就能把椭圆「抬」圆。': 'Apogee is slowest; a little extra speed here lifts the ellipse into a circle.', '现在跑得偏快，稍微减一点，椭圆就会变圆。': "You're a bit fast now; slow down slightly and the ellipse circularizes.", '在近地点加速，远地点会被抬高；到了远地点还要再补一次。': 'Accelerate at perigee to raise the apogee; another burn awaits at apogee.', '近地点加速后，椭圆的远端会一路延伸到月球轨道。': "After the perigee burn, the far end of the ellipse stretches all the way to the Moon's orbit.", '当地速度达到逃逸速度，轨迹就从椭圆变成不再闭合的双曲线。': 'At local escape velocity the path changes from a closed ellipse to an open hyperbola.', '第三宇宙速度约 16.7 km/s，到这里连太阳也拉不住它。': "The third cosmic velocity is about 16.7 km/s - beyond it even the Sun can't hold the craft.", '① 调速度': '① Speed', '② 点火与演示': '② Ignite & demo', '③ 观察工具': '③ Observation', '用推荐速度': 'Use best', '清除预览': 'Clear', '在轨迹上选点': 'Pick on trail', '取消选点': 'Cancel picking', '跳到推荐点': 'Go to point', '自动演示': 'Auto demo', '复位视角': 'Reset view', '保存轨道快照': 'Save snapshot', '空': 'empty', '速度参考线：7.9 环绕地球   11.2 脱离地球   16.7 飞出太阳系': 'Reference lines: 7.9 orbit Earth   11.2 escape Earth   16.7 leave the Solar System', '绿色 = 本任务合理区间 {a} {b}': 'Green = reasonable range for this task {a} {b}', '仿真倍速（最高 16×）': 'Sim speed (up to 16×)', '空格=暂停    Enter=点火    R=重来    H=讲解    F=受力分析    滚轮=缩放    拖动画面=平移': 'Space=pause   Enter=fire   R=reset   H=lesson   F=forces   L=EN/中文   wheel=zoom   drag=pan', '近/远地点标注': 'Apsis markers', '速度箭头': 'Velocity arrow', '点火前对比': 'Pre-burn compare', '视角跟随': 'Follow view', '沉浸模式：面板已收起，滚轮缩放 / 按住左键拖动平移 / 按 V 或 Esc 退出': 'Immersive mode: panels hidden - wheel to zoom, drag to pan, V or Esc to exit', '视角已复位：可以看到完整的地月尺度（拖动画面还能平移）': 'View reset: full Earth-Moon scale (drag to pan)', '受力分析已打开：白=合力，蓝/紫=地球/月球引力，虚线=切向(改速率)与法向(改方向)': 'Force analysis on: white=net, blue/purple=Earth/Moon gravity, dashed=tangential(speed)/normal(direction)', '受力分析已关闭（按 F 重新打开）': 'Force analysis off (press F to reopen)', '已打开讲解：{a}': 'Lesson opened: {a}', '已切换到任务 {a}：{b}，飞船回到起点轨道': 'Switched to task {a}: {b} - spacecraft back to the start orbit', '飞船已经撞上{a}，请点「重新发射」再来一次': 'The craft has hit the {a} - click Relaunch to try again', '飞船已经撞上{a}，请先点「重新发射」': 'The craft has hit the {a} - click Relaunch first', '请输入数字，例如 7.90（单位 km/s）': 'Enter a number, e.g. 7.90 (km/s)', '速度要大于 0、不超过 {a:g} km/s': 'Speed must be > 0 and at most {a:g} km/s', '已填入推荐速度 {a:.2f} km/s，看虚线满意了再点火': 'Filled in recommended {a:.2f} km/s - fire when the preview looks right', '暂时找不到推荐点，先让飞船飞一会儿再试': "Can't find the recommended point yet - let the craft fly a while first", '已跳到{a}，推荐速度约 {b:.2f} km/s': 'Jumped to {a}, recommended ≈ {b:.2f} km/s', '请在左侧轨迹线上点击，选下一次点火的位置': 'Click on the trail at left to pick the next burn position', '已经在平移视角了：拖动改变位置，滚轮缩放，「复位视角」回到全景': 'Already panning: drag to move, wheel to zoom, Reset view for the full scene', '还没有可点的轨迹，先点火让飞船飞一段': 'No trail to click yet - fire first and let it fly', '要点在轨迹线上哦，再靠近一点': 'Click on the trail - get a bit closer', '点火位置已选定，下一步调速度再点火': 'Burn position selected - set the speed, then fire', '视角跟随已打开：飞船靠近边缘时画面会自动跟过去': 'Follow view on: the camera follows the ship near the edges', '已保存快照，最多留 3 张用于对比': 'Snapshot saved - up to 3 kept for comparison', '自动演示：第 1 步已把远地点抬到同步轨道，到第 2 步会自动修圆': 'Auto demo: step 1 raised the apogee to GEO radius; step 2 will circularize automatically', '自动演示：已在{a}以 {b:.2f} km/s 点火': 'Auto demo: fired at {a} with {b:.2f} km/s', '自动演示：已在远地点补速，同步圆轨道完成！注意它的周期 ≈ 24 小时': 'Auto demo: circularized at apogee - GEO done! Note its period ≈ 24 h', '自动演示快进：真实转移要飞约 5 天，这里直接跳到近月点 {a:,.0f} km 高度刹车': 'Auto demo fast-forward: the real transfer takes about 5 days - jumping straight to perilune at {a:,.0f} km to brake', '自动演示：已在环月近月点减速，修成环月圆轨道': 'Auto demo: slowed at lunar perilune - circular lunar orbit complete', '自动演示第 2 步：在远地点补速，把椭圆修成 1200 km 圆轨道': 'Auto demo step 2: add speed at apogee to make the 1200 km circular orbit', '自动演示第 3 步：在高轨道减速，把近地点压到 300 km': 'Auto demo step 3: slow down in the high orbit to push perigee to 300 km', '自动演示第 4 步：在近地点减速，修成 300 km 圆轨道': 'Auto demo step 4: slow at perigee to finish the 300 km circular orbit', '第 1 步达成！远地点已到同步轨道，接下来在远地点补速把椭圆修圆': 'Step 1 done! Apogee at GEO radius - now add speed at apogee to circularize', '已进入月球引力范围！现在必须刹车减速，否则只是擦肩而过（速度滑块已改为相对月球）': "Entered the Moon's gravity! Brake now or you'll just fly past (slider now shows speed relative to the Moon)", '捕获成功！现在是绕月大椭圆，还要在拱点再减速才能修成环月圆轨道': 'Captured! Now on a big lunar ellipse - brake again at an apsis to circularize', '第 1 步达成：远地点抬到 1200 km。现在飞到远地点补速，把椭圆修圆': 'Step 1 done: apogee at 1200 km. Fly to apogee and add speed to circularize', '第 2 步达成：1200 km 圆轨道。接下来在高轨道减速降轨': 'Step 2 done: 1200 km circular orbit. Next, slow down to lower the orbit', '第 3 步达成：近地点降到 300 km。最后飞到近地点再减速修圆': 'Step 3 done: perigee down to 300 km. Finally slow at perigee to circularize', '闯关成功！你完成了「{a}」': 'Mission complete! You finished "{a}"', '五个任务全部完成，你已经掌握速度如何决定轨道形状': 'All tasks complete - you now know how speed decides the shape of an orbit', '飞船撞上了{a}。速度太小，引力把它拉了回来，试试「重新发射」': 'The craft hit the {a}. Speed too low - gravity pulled it back. Try Relaunch', '现在是任务 1：起始轨道偏椭圆，试着调速度把它修圆（按 H 看讲解）': 'Task 1: the starting orbit is elliptical - adjust the speed to circularize it (press H for the lesson)', '自动演示标准解：这就是界面各区域的真实样子': 'Auto-demo standard solution: this is what each UI region really looks like', '讲解页：为什么用这个速度、合理区间和真实航天任务': 'Lesson page: why this speed, the reasonable range, and real missions', '受力分析：白=合力，蓝/紫=地球/月球引力，虚线=切向(改速率)与法向(改方向)': 'Force analysis: white=net, blue/purple=Earth/Moon gravity, dashed=tangential(speed)/normal(direction)', '任务 3 通关：近月制动被捕获，再在近月点减速修成环月圆轨道': 'Task 3 complete: captured by lunar braking, then circularized at perilune', '已被月球捕获：环月轨道近月点 {a:,.0f} km，e = {b:.2f}': 'Captured by the Moon: perilune {a:,.0f} km, e = {b:.2f}', '还没被月球捕获：相对月球速度仍超过逃逸速度，会飞掠而过，要继续减速': 'Not captured yet: speed relative to the Moon still exceeds escape - it will fly past; keep slowing down', '已达第三宇宙速度，太阳也拉不住它了': "Third cosmic velocity reached - even the Sun can't hold it now", '已达第二宇宙速度，可以飞离地球': 'Second cosmic velocity reached - the craft can leave Earth', '速度变大，轨道远端被抬高': 'Speed increased: the far end of the orbit rises', '速度变小，轨道会往地球这边塌': 'Speed decreased: the orbit sags toward Earth', '已暂停，趁现在看清轨道形状': 'Paused - take a good look at the orbit shape'}
MU_EARTH = 398600.4418
MU_MOON = 4902.800066
R_EARTH = 6378.137
R_MOON = 1737.4
MOON_ORBIT_RADIUS = 384400.0
MOON_ORBIT_PERIOD = 2360591.5104
MOON_ANGULAR_SPEED = 2 * np.pi / MOON_ORBIT_PERIOD
MOON_SOI_RADIUS = 66100.0
HIGH_ORBIT_ALT = 1200.0
LOW_ORBIT_ALT = 300.0
HIGH_ORBIT_R = R_EARTH + HIGH_ORBIT_ALT
LOW_ORBIT_R = R_EARTH + LOW_ORBIT_ALT
LUNAR_SOI_ENTER = 30000.0
LUNAR_WORK_ALT = 500.0
LUNAR_BURN_TOL = 0.05
SLIDER_MIN_SPEED = 0.05
V1 = 7.9
V2 = 11.2
V3 = 16.7
LAUNCH_ANGLE = 0.0
LAUNCH_ALTITUDE = 200.0
NEAR_ORBIT_RADIUS = R_EARTH + 400.0
SYNC_ORBIT_RADIUS = 42164.0
MOON_TEXTURE_SCALE = 2.4
MAX_INPUT_SPEED = 40.0
SPEED_SLIDER_MAX = 25.0
MIN_VIEW_SPAN = 12000.0
MAX_VIEW_SPAN = 4000000.0
COAST_FRAME_SECONDS = 7.5
MAX_INTEGRATION_STEP = 5.0
ANIMATION_INTERVAL_MS = 33
FULL_REDRAW_EVERY = 600
STALL_GUARD_SECONDS = 0.25
RATE_MIN, RATE_MAX, RATE_STEP = 0.25, 16.0, 0.25
RATE_PRESETS = (1.0, 4.0, 8.0, 16.0)
PREDICT_MIN_STEP = 30.0
PREDICT_MAX_STEP = 2400.0
PREDICT_BASE_STEP = 90.0
PREDICT_REF_INTERVAL = 0.16
TRAIL_MAX_POINTS = 2600
TRAIL_MIN_GAP = 260.0
BLIT_RECTS = ((0.0, 0.345, 0.655, 0.945), (0.04, 0.208, 0.34, 0.266), (0.648, 0.338, 0.972, 0.938))
CARD_REDRAW_EVERY = 10
MAX_RENDER_PIXELS = 2600000
FORCE_PANEL_X = 0.028
FORCE_PANEL_Y = 0.395
FORCE_PANEL_W = 0.3
FORCE_PANEL_H = 0.215
FORCE_LINE_H = 0.0192
FORCE_PANEL_ROWS = 9
_TRANSFER_R = R_EARTH + LAUNCH_ALTITUDE
_TRANSFER_A = (_TRANSFER_R + MOON_ORBIT_RADIUS) / 2
_TRANSFER_HALF_T = np.pi * np.sqrt(_TRANSFER_A ** 3 / MU_EARTH)
MOON_INITIAL_ANGLE = np.pi - MOON_ANGULAR_SPEED * _TRANSFER_HALF_T
C_SPACE = '#04070d'
C_PANEL = '#0c1521'
C_PANEL2 = '#121e2c'
C_EDGE = '#2b3d52'
C_TEXT = '#e9f3fd'
C_DIM = '#92a8bd'
C_BLUE = '#3fa7ff'
C_CYAN = '#4fd8ff'
C_GREEN = '#5fe0a0'
C_AMBER = '#ffc861'
C_RED = '#ff6b6b'
C_PURPLE = '#c792ea'
C_TRAIL = '#ff7a5c'
HOME_SPAN_Y = 1150000.0
HOME_UP_FRAC = 0.11

def moon_position(t):
    '''圆轨道近似下的月球位置与速度。'''

    angle = MOON_INITIAL_ANGLE + MOON_ANGULAR_SPEED * t
    pos = np.array([MOON_ORBIT_RADIUS * np.cos(angle), MOON_ORBIT_RADIUS * np.sin(angle)])
    vel = MOON_ANGULAR_SPEED * np.array([-pos[1], pos[0]])
    return pos, vel

def gravity_acceleration(px, py, t):
    '''地球 + 月球引力；在天体内部限制奇点，由碰撞逻辑截断。'''

    pos = np.array([px, py], dtype=float)
    earth_r = max(np.linalg.norm(pos), R_EARTH)
    acc_earth = -MU_EARTH * pos / earth_r ** 3
    moon_pos, _ = moon_position(t)
    delta = moon_pos - pos
    moon_r = max(np.linalg.norm(delta), R_MOON)
    acc_moon = MU_MOON * delta / moon_r ** 3
    return acc_earth + acc_moon

def orbit_elements(px, py, pvx, pvy):
    '''相对地球的机械能、偏心率、半长轴。'''

    r = max(np.hypot(px, py), R_EARTH)
    v2 = pvx * pvx + pvy * pvy
    energy = v2 / 2 - MU_EARTH / r
    h = px * pvy - py * pvx
    ecc = np.sqrt(max(1 + 2 * energy * h ** 2 / MU_EARTH ** 2, 0.0))
    semi = -MU_EARTH / (2 * energy) if energy < 0 else np.inf
    return energy, ecc, semi

def apoapsis_periapsis(px, py, pvx, pvy):
    '''返回（近地点，远地点）半径；逃逸时远地点为 inf。'''

    energy, ecc, semi = orbit_elements(px, py, pvx, pvy)
    if energy >= 0:
        peri = semi if np.isfinite(semi) else np.inf
        return max(np.hypot(px, py), R_EARTH), np.inf, energy, ecc
    peri = semi * (1 - ecc)
    apo = semi * (1 + ecc)
    return peri, apo, energy, ecc

def orbit_period(semi):
    if np.isfinite(semi):
        return 2 * np.pi * np.sqrt(semi ** 3 / MU_EARTH)
    return np.inf

def classify_orbit(px, py, pvx, pvy, t):
    '''用易懂规则给出当前主要轨道类型。'''

    vel = np.array([pvx, pvy], dtype=float)
    pos = np.array([px, py], dtype=float)
    earth_speed = np.linalg.norm(vel)
    energy, ecc, _ = orbit_elements(px, py, pvx, pvy)
    moon_pos, moon_vel = moon_position(t)
    moon_dist = np.linalg.norm(pos - moon_pos)
    rel = vel - moon_vel
    moon_energy = float(np.dot(rel, rel)) / 2 - MU_MOON / max(moon_dist, R_MOON)
    if moon_dist < MOON_SOI_RADIUS and moon_energy < 0:
        if moon_relative_elements(px, py, pvx, pvy, t)[3] < 0.15:
            return T('环月圆轨道')
        return T('环月椭圆轨道')
    if earth_speed >= V3:
        return T('飞出太阳系')
    if energy >= 0:
        return T('脱离地球')
    if ecc < 0.06:
        return T('圆轨道')
    return T('椭圆轨道')

def integrate_trajectory(px, py, pvx, pvy, t0, steps, total_time=None):
    '''
    自适应步长 RK2（中点法）积分，撞到天体即停止。
    近地点用小步长保证精度，远地点放大步长以覆盖完整周期。
    '''

    xs, ys, vxs, vys, ts = [], [], [], [], []
    pos = np.array([px, py], dtype=float)
    vel = np.array([pvx, pvy], dtype=float)
    t = float(t0)
    elapsed = 0.0
    for _ in range(steps):
        r = max(np.linalg.norm(pos), R_EARTH)
        moon_pos, _ = moon_position(t)
        r_moon = max(np.linalg.norm(pos - moon_pos), R_MOON)
        r_ref = min(r, r_moon * 1.5)
        dt = PREDICT_BASE_STEP * (r_ref / (R_EARTH + LAUNCH_ALTITUDE)) ** 1.5
        dt = float(np.clip(dt, PREDICT_MIN_STEP, PREDICT_MAX_STEP))
        if total_time is not None and elapsed + dt > total_time:
            break
        a0 = gravity_acceleration(pos[0], pos[1], t)
        v_half = vel + a0 * (dt / 2)
        nxt = pos + v_half * dt
        tn = t + dt
        moon_pos, _ = moon_position(tn)
        if np.linalg.norm(nxt) <= R_EARTH or np.linalg.norm(nxt - moon_pos) <= R_MOON:
            break
        a1 = gravity_acceleration(nxt[0], nxt[1], tn)
        vel = v_half + a1 * (dt / 2)
        pos = nxt
        t = tn
        elapsed += dt
        xs.append(pos[0])
        ys.append(pos[1])
        vxs.append(vel[0])
        vys.append(vel[1])
        ts.append(t)
        continue
    return np.asarray(xs), np.asarray(ys), np.asarray(vxs), np.asarray(vys), np.asarray(ts)

def predict_full_orbit(px, py, pvx, pvy, t0, steps=3200):
    '''预判未来轨迹，至少覆盖一个完整周期（逃逸时按 12 天截断）。'''

    r_rel, _, e_rel, _, _, _ = moon_relative_elements(px, py, pvx, pvy, t0)
    if r_rel < MOON_SOI_RADIUS and e_rel < 0:
        a_moon = -MU_MOON / (2 * e_rel)
        period = 2 * np.pi * np.sqrt(a_moon ** 3 / MU_MOON)
        total = float(np.clip(1.15 * period, 7200.0, 345600.0))
    else:
        _, _, semi = orbit_elements(px, py, pvx, pvy)
        period = orbit_period(semi)
        total = min(1.05 * period, 1036800.0) if np.isfinite(period) else 518400.0
        total = max(total, 86400.0)
    return integrate_trajectory(px, py, pvx, pvy, t0, steps, total_time=total)

def _globe_texture(kind, size=320, seed=7):
    '''极简程序化地球/月球贴图，RGBA，圆外 alpha=0。'''

    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[-1:1:size * (0.0+1.0j), -1:1:size * (0.0+1.0j)]
    rr = np.hypot(xx, yy)
    img = np.zeros((size, size, 4))
    mask = rr <= 1.0
    if kind == 'earth':
        base = np.array([0.13, 0.36, 0.62])
        land = np.array([0.2, 0.52, 0.28])
        grid = 8
        noise = rng.normal(0, 1, (grid, grid))
        noise = np.kron(noise, np.ones((size // grid + 1, size // grid + 1)))[:size, :size]
        img[(..., 0)] = np.where(noise > 0.15, land[0], base[0])
        img[(..., 1)] = np.where(noise > 0.15, land[1], base[1])
        img[(..., 2)] = np.where(noise > 0.15, land[2], base[2])
        img[(..., 0)] += np.clip((np.abs(yy) - 0.8) * 5, 0, 1) * 0.7
        img[(..., 1)] += np.clip((np.abs(yy) - 0.8) * 5, 0, 1) * 0.7
        img[(..., 2)] += np.clip((np.abs(yy) - 0.8) * 5, 0, 1) * 0.7
    else:
        g = 0.66 + rng.normal(0, 0.05, (size, size))
        img[(..., 0)] = img[(..., 1)] = img[(..., 2)] = np.clip(g, 0, 1)
        for _ in range(70):
            cy, cx = rng.uniform(-0.95, 0.95, 2)
            rad = rng.uniform(0.02, 0.1)
            d = np.hypot(xx - cx, yy - cy)
            img[..., 0:3] = img[..., 0:3] - 0.18 * ((d < rad) & (d > rad * 0.55))
    shade = np.clip(1.25 - 0.75 * np.clip(rr, 0, 1.6) ** 2, 0.25, 1.0)
    img[..., 0:3] = np.clip(img[..., 0:3] * shade[(..., None)], 0, 1)
    img[(..., 3)] = mask.astype(float)
    return img

def app_dir():
    '''资源根目录。打包成 exe 时 sys._MEIPASS 指向临时解压目录，
    直接开发运行时退回脚本所在目录。'''

    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))

def load_texture(filename, fallback_kind):
    '''依次在工作目录、脚本目录、assets、图片 目录寻找贴图。'''

    here = Path(__file__).resolve().parent
    bundle = app_dir()
    candidates = Path.cwd() / filename, here / filename, here / 'assets' / filename, bundle / 'assets' / filename, bundle / filename, Path.cwd() / 'assets' / filename, here / '图片' / filename, Path.cwd() / '图片' / filename
    for path in candidates:
        if path.is_file():
            return plt.imread(path), path
    return _globe_texture(fallback_kind), None

TASK_COUNT = 6
TASK_NAMES = ['近地圆轨道', '地球同步轨道', '地月转移轨道', '脱离地球', '飞出太阳系', '变轨与降轨']
TASK_ICONS = ['①', '②', '③', '④', '⑤', '⑥']
TASK_SHORT = ['环绕', '同步', '奔月', '离地', '出系', '变轨']
TASK_GOALS = ['把椭圆轨道修圆：让它稳定绕地球飞行，不再忽高忽低。', '分两步升到同步轨道：先抬高远地点，再在远地点把椭圆修圆。', '先转移去月球，再近月制动被捕获，最后修成环月圆轨道。', '把速度加到逃逸速度以上，让飞船不再被地球拉回来。', '把速度加到第三宇宙速度以上，飞出太阳系。', '先升到 1200 km 圆轨道，再降回 300 km 圆轨道：加速升轨、减速降轨，每次都要再点火修圆。']
TASK_PHASE_NAMES = [['修圆'], ['抬远地点', '远地点修圆'], ['地月转移', '近月制动', '环月修圆'], ['逃逸'], ['飞出太阳系'], ['加速升轨', '远地点修圆', '减速降轨', '近地点修圆']]

def phase_name(index=None, phase=None):
    '''当前（或指定）任务阶段的名称（跟随界面语言），超出范围时退回最后一项。'''

    i = current_task if index is None else index
    p = task_phase if phase is None else phase
    names = TASK_PHASE_NAMES[i]
    return T(names[min(p, len(names) - 1)])

TASK_LESSON = [{'core': '引力刚好当向心力，不多也不少', 'body': ['飞船其实一直在「往下掉」，但地球表面也在往下弯。', '横向速度刚好时，每秒下落的距离 = 地面弯下去的距离。', '慢了：引力占上风，轨道朝地球一侧塌陷，近地点变低。', '快了：惯性占上风，飞船被甩出去，圆被拉成长椭圆。', '由 GMm/r² = mv²/r 两边化简，得 v = √(GM/r)。', '代入 200 km 高度 ≈ 7.78 km/s（课本 7.9 是地面值）。'], 'range_note': '低于下限，近地点会扎进大气层坠毁；高于上限，圆被拉成椭圆，开始忽高忽低。', 'cases': [('中国空间站「天宫」', '轨道高约 400 km，速度约 7.68 km/s，约 90 分钟绕地球一圈。'), ('神舟载人飞船', '与空间站保持同一高度和速度，才能慢慢靠近完成对接。'), ('遥感 / 气象卫星', '多运行在 500~800 km 的太阳同步轨道，绕一圈约 100 分钟。')], 'trivia': '牛顿大炮：炮弹达到 7.9 km/s 就永远落不了地 —— 这就是第一宇宙速度。'}, {'core': '周期必须等于地球自转一圈（23 时 56 分 04 秒）', 'body': ['开普勒第三定律算死半径：约 42,164 km（离地 35,786 km）。', '为什么不能直飞上去？一路对抗引力，燃料贵得多。', '霍曼转移：先在近地点加速，把远地点抬到同步高度。', '到远地点时速度只剩约 1.60 km/s，而圆轨道要 3.07。', '所以在远地点第二次点火补速，把椭圆重新修圆。', '两次点火合计比一次直推省燃料，是真实任务标准做法。'], 'range_note': '第 1 步偏小够不到同步高度，偏大会逃逸；第 2 步偏小会回落，偏大轨道又变扁。', 'cases': [('北斗三号 GEO 卫星', '定点在赤道上空约 35,786 km，始终对着同一片区域提供服务。'), ('风云四号气象卫星', '静止在同一片天空，可以对同一区域做 24 小时连续观测。'), ('通信 / 广播卫星', '正因为它相对地面「不动」，家里的卫星天线锅才能固定朝一个方向。')], 'trivia': '同步卫星必须在赤道上空：轨道面与赤道面重合，才能相对地面静止。'}, {'core': '把远地点拉到月球轨道上，还要算准到达时间', 'body': ['目标：椭圆远地点 = 月球公转半径 384,400 km。', '半长轴 a =（近地点 + 384,400）/ 2 ≈ 195,489 km。', '活力公式 v = √(μ(2/r − 1/a)) → 近地点约 10.92 km/s。', '开普勒第三定律：飞行时间 = 半个周期 ≈ 5 天。', '起飞时刻要算准：飞船到远地点时月球也刚好到那里。', '到月球附近被引力加速到约 2.4 km/s，须刹车被捕获。'], 'range_note': '慢了够不到月球轨道、半路被拉回；快了会越过月球轨道、错过交会窗口。', 'cases': [('嫦娥一号（2007）', '地月转移飞行 114 小时、行程 43.66 万公里，之后完成首次近月制动。'), ('首次近月制动', '近月点约 2.4 km/s，须减到约 2.0 km/s 才被月球捕获。'), ('阿波罗 11 号（1969）', '走得更「陡」的自由返回轨道，约 3 天抵达月球附近。')], 'trivia': '月亮不掉下来的原理和飞船一样：它也在横向高速运动，永远「差一点」落地。', 'phase_lesson': [{}, {'core': '飞到月球附近必须刹车，否则只是擦肩而过', 'body': ['不减速的话，飞船相对月球是双曲线轨道：绕过月球又飞走。', '判断标准：相对月球的比机械能 ε = v²/2 − GM月/r。', 'ε ≥ 0：抓不住，只是飞掠；ε < 0：被月球捕获，开始绕月。', '刹车要在近月点做：那里相对速度最大，减速最省燃料。', '本模拟器是二维简化，交会距离比真实任务远，制动量偏大。', '速度滑块此刻显示的是**相对月球**的速度，不再是地心速度。'], 'range_note': '减得不够就抓不住，会被月球甩回地球方向；减过头会直接撞上月面。', 'cases': [('嫦娥一号首次近月制动', '2007 年 11 月 5 日，近月点约 2.4 km/s 减到约 2.0，进入环月轨道。'), ('阿波罗 11 号 LOI', '在月球背面点火减速约 0.9 km/s，进入约 110 km 环月轨道。'), ('嫦娥五号（2020）', '两次近月制动 + 轨道修正，最后降到 200 km 环月圆轨道。')], 'trivia': '近月制动都在月球背面做：那时地面测控中断，飞船必须自主完成。'}, {'core': '在近月点（或远月点）再点一次火，把大椭圆修成圆轨道', 'body': ['只刹车一次得到的是大椭圆环月轨道，不是工作轨道。', '通法：在某个拱点点火，把「对面那个点」拉到目标高度。', '在远月点减速 → 近月点被压低；在近月点减速 → 远月点被压低。', '来回两次，椭圆就收敛成目标高度的圆轨道。', '圆轨道判据：相对月球的偏心率 e < 0.15。', '最终速度就是该高度的环月速度 v = √(GM月/r)。'], 'range_note': '近月点减过头会让轨道另一头扎进月面；减不足则仍是扁椭圆。', 'cases': [('嫦娥一号降轨', '12 小时轨道 → 3.5 小时 → 127 分钟圆轨道，共三次制动。'), ('月球轨道器 / LRO', '先入 大椭圆，再多次降轨到约 50 km 极轨做测绘。'), ('阿波罗指令舱', '停在约 110 km 环月圆轨道，等待登月舱上升返回交会。')], 'trivia': '月球没有大气，不能靠「气动刹车」降轨，每次降轨都要烧燃料。'}]}, {'core': '让机械能 ≥ 0 —— 引力再也追不上', 'body': ['比机械能 ε = v²/2 − μ/r，判断束缚与否的尺子。', 'ε < 0：被引力拴住，沿闭合椭圆绕圈，飞多远都回来。', 'ε ≥ 0：轨迹变成张开的双曲线，一去不回头。', '令 ε = 0 得逃逸速度 v = √(2μ/r) = √2 × 圆轨道速度。', '本题 200 km 高度 ≈ 11.01 km/s；地面即课本的 11.2。', '逃逸 ≠ 没有引力 —— 引力还在拉，只是拉不回来。'], 'range_note': '低于逃逸速度，飞多远都会被拉回；一旦超过，高度只增不减。', 'cases': [('天问一号（2021）', '飞往火星，必须先把速度加到超过逃逸速度才能离开地球。'), ('月球 / 火星探测任务', '都先打进逃逸或大椭圆转移轨道，再择机修正、制动。'), ('木星、土星深空探测', '离开地球后再借行星引力弹弓接力加速，省下大量燃料。')], 'trivia': '逃逸速度与质量无关：乒乓球和飞船同高同速，轨迹完全一样。'}, {'core': '逃出地球还不够，还得从太阳手里逃出去', 'body': ['离开地球后，飞船仍然被太阳牢牢拉着。', '不过地球以 29.8 km/s 绕太阳跑，这份速度可以直接继承。', '在地球轨道处逃离太阳，日心速度需 √2 × 29.8 ≈ 42.1。', '两笔账合起来（克服地球引力 + 剩余日心速度），地面出发约 16.7。', '这就是第三宇宙速度 —— 不是简单乘 √2 得来的。', '现实中靠行星引力弹弓接力加速，不必一次带足燃料。'], 'range_note': '低于 16.7 km/s，飞船最终会被太阳留在某条绕日椭圆轨道上，飞不出太阳系。', 'cases': [('旅行者 1 号（1977 发射）', '相对太阳约 17 km/s，2012 年进入星际空间，是飞得最远的人造物体。'), ('旅行者 2 号', '相对太阳约 15 km/s，2018 年进入星际空间，唯一造访过天王星与海王星。'), ('先驱者 10 / 11 号、新视野号', '连同两艘旅行者，共 5 个探测器正在飞出太阳系。')], 'trivia': '引力弹弓：从行星背后掠过，借行星公转动量加速，几乎不费燃料。'}, {'core': '加速抬高对面、减速压低对面；想变圆就得在另一个拱点再点一次火', 'body': ['加速：点火这一侧变成近地点，对面被抬高 —— 轨道变大变扁。', '减速：点火这一侧变成远地点，对面被压低 —— 轨道变小变扁。', '只点一次火得到的一定是椭圆，不会是圆轨道。', '要修圆，必须跑到椭圆的另一端再点火，把对面拉回来。', '升轨两次都加速；降轨两次都减速 —— 这就是霍曼转移的正反两用。', '越高的圆轨道跑得越慢：v = √(GM/r)，高度决定速度。'], 'range_note': '偏小上不去 / 降不下来，偏大会冲过目标高度，或把轨道拉得更扁。', 'cases': [('北斗 / GPS 卫星入轨', '火箭先把卫星送进转移椭圆，卫星再在远地点点火把自己修圆。'), ('空间站定期抬轨', '货运飞船点火补速，抵消稀薄大气阻力造成的缓慢降轨。'), ('神舟 / 飞船返回', '先反向点火减速降轨，让近地点扎进大气层，再受控再入。')], 'trivia': '降轨要减速、升轨要加速 —— 听起来反直觉，因为减速反而让轨道变小。', 'phase_lesson': [{'core': '在近地点加速：这一端不动，对面（远地点）被抬高', 'body': ['点火点一定是新轨道的近地点：这里速度最快，加速最划算。', '活力公式 v = √(GM(2/r − 1/a))，a =（近 + 远）/ 2。', '本题从 200 km 抬到 1200 km，近地点约需 8.05 km/s。', '加速后轨道变成 200 km × 1200 km 的椭圆。', '注意：这一瞬间飞船的高度没变，变的是轨道形状。', '下一步要飞到远地点再点火，才能把这个椭圆修圆。'], 'range_note': '慢了远地点够不到 1200 km；快了会冲过头，甚至接近逃逸。'}, {'core': '飞到远地点补速，把椭圆「撑」成圆', 'body': ['远地点是整条椭圆上跑得最慢的地方（约 6.99 km/s）。', '那里圆轨道需要的速度是 7.25 km/s，还差一点。', '补上这 0.26 km/s，近地点被抬到和远地点一样高 → 圆。', '判据就是偏心率 e < 0.05。', '这一步叫「远地点变轨」，是地球同步卫星入轨的标准动作。', '两次点火合计比一次直推省燃料，这是霍曼转移的精髓。'], 'range_note': '补少了仍是椭圆，补多了会把近地点抬得比远地点还高，又变扁。'}, {'core': '在高轨道减速：这一端变远地点，对面（近地点）被压低', 'body': ['减速和加速完全对称，只是方向相反。', '在 1200 km 圆轨道上反向点火，这一侧立刻变成远地点。', '减到约 7.02 km/s，对面就落到 300 km。', '轨道变成 300 km × 1200 km 的椭圆。', '飞船高度此刻还是 1200 km —— 变的是对面。', '降轨为什么能返回？就是靠这一步把近地点压进大气层。'], 'range_note': '减得不够降不下来；减过头近地点扎进大气层，就回不来了。'}, {'core': '飞到近地点再减速，把椭圆「削」成圆', 'body': ['近地点是椭圆上跑得最快的地方（约 7.96 km/s）。', '那里 300 km 圆轨道只需要 7.61 km/s，多了 0.35。', '减掉这部分，远地点被压到和近地点一样高 → 圆。', '再判一次偏心率 e < 0.05 就算完成。', '至此飞船比出发时低了 100 km，而且跑得更快了。', '记住结论：低轨跑得快、高轨跑得慢（开普勒第三定律）。'], 'range_note': '减少了仍是椭圆，减多了远地点会低于近地点，把飞船压向大气层。'}]}]
TASK_LESSON_EN = [{'core': 'Gravity acts exactly as the centripetal force - no more, no less', 'body': ["The spacecraft is really always 'falling', but Earth's surface curves away beneath it.", 'At exactly the right horizontal speed, the fall per second equals how much the ground curves away.', 'Too slow: gravity wins, the orbit collapses toward Earth and the perigee drops.', 'Too fast: inertia wins, the craft is flung out and the circle stretches into an ellipse.', 'From GMm/r² = mv²/r, cancel m and get v = √(GM/r).', 'At 200 km altitude that is ≈ 7.78 km/s (the textbook 7.9 is the ground-level value).'], 'range_note': 'Below the lower bound the perigee dips into the atmosphere and burns up; above it, the circle stretches into an ellipse and the altitude starts to wobble.', 'cases': [("Chinese space station 'Tiangong'", 'Orbits at about 400 km at roughly 7.68 km/s, circling Earth about every 90 minutes.'), ('Shenzhou crewed spacecraft', "Matches the station's altitude and speed so it can approach slowly and dock."), ('Remote-sensing / weather satellites', 'Mostly in 500-800 km Sun-synchronous orbits, one lap about every 100 minutes.')], 'trivia': "Newton's cannon: a shell at 7.9 km/s never lands - that is the first cosmic velocity."}, {'core': 'The period must equal one rotation of Earth (23 h 56 min 04 s)', 'body': ["Kepler's third law fixes the radius: about 42,164 km (35,786 km altitude).", 'Why not fly straight up? Fighting gravity the whole way costs far more fuel.', 'Hohmann transfer: first burn at perigee to lift the apogee to GEO height.', 'At apogee the speed is only about 1.60 km/s, while a circular orbit needs 3.07.', 'So a second burn at apogee tops up the speed and re-circularizes the ellipse.', 'Two burns together beat one direct push on fuel - the standard practice on real missions.'], 'range_note': 'Step 1: too low never reaches GEO, too high escapes; step 2: too low falls back, too high flattens the orbit again.', 'cases': [('BeiDou-3 GEO satellites', 'Parked about 35,786 km above the equator, serving the same region around the clock.'), ('Fengyun-4 weather satellites', 'Fixed over one patch of sky, watching the same region 24 hours a day.'), ('Communication / broadcast satellites', "Because they seem 'motionless' from the ground, home dish antennas can point one way forever.")], 'trivia': 'A geostationary satellite must sit over the equator: only with the orbit plane matching the equator can it stay fixed overhead.'}, {'core': "Stretch the apogee to the Moon's orbit, and time the arrival precisely", 'body': ['Target: ellipse apogee = lunar orbit radius 384,400 km.', 'Semi-major axis a = (perigee + 384,400)/2 ≈ 195,489 km.', 'Vis-viva v = √(μ(2/r − 1/a)) → about 10.92 km/s at perigee.', "Kepler's third law: flight time = half the period ≈ 5 days.", 'Launch timing must be exact: the Moon arrives at the apogee just as the craft does.', 'Near the Moon, gravity speeds it up to about 2.4 km/s - it must brake to be captured.'], 'range_note': "Too slow never reaches the Moon's orbit and gets pulled back halfway; too fast overshoots and misses the encounter window.", 'cases': [("Chang'e-1 (2007)", "Flew a 114-hour, 436,600 km trans-lunar cruise, then performed China's first lunar braking burn."), ('First lunar braking burn', 'From about 2.4 km/s at perilune down to about 2.0 km/s to be captured.'), ('Apollo 11 (1969)', 'Took the steeper free-return trajectory, reaching the Moon in about 3 days.')], 'trivia': "The Moon stays up for the same reason: it moves sideways so fast it keeps 'missing' the ground.", 'phase_lesson': [{}, {'core': 'You must brake near the Moon, or you merely fly past it', 'body': ['Without slowing down, the path relative to the Moon is a hyperbola: swing by and leave.', 'The test: specific mechanical energy relative to the Moon, ε = v²/2 − GM_moon/r.', 'ε ≥ 0: not captured, just a flyby; ε < 0: captured, now orbiting the Moon.', 'Brake at perilune: relative speed is highest there, so slowing costs the least fuel.', 'This simulator is a 2-D simplification; the encounter geometry is farther out than real missions.', 'The speed slider now shows the speed relative to the Moon, not the geocentric speed.'], 'range_note': 'Too little braking and the Moon flings you back toward Earth; too much and you dive straight into the surface.', 'cases': [("Chang'e-1 first lunar braking", 'On 5 Nov 2007, from about 2.4 km/s to about 2.0 at perilune, entering lunar orbit.'), ('Apollo 11 LOI', 'Burned about 0.9 km/s on the far side, entering a roughly 110 km lunar orbit.'), ("Chang'e-5 (2020)", 'Two braking burns plus corrections, ending in a 200 km circular lunar orbit.')], 'trivia': 'Lunar braking happens on the far side: with radio contact blocked, the spacecraft must do it autonomously.'}, {'core': 'Burn again at an apsis to reshape the big ellipse into a circle', 'body': ['A single braking burn leaves a large lunar ellipse, not a working orbit.', "General rule: burn at one apsis to move 'the opposite point' to the target height.", 'Slow at apolune → perilune drops; slow at perilune → apolune drops.', 'Two passes and the ellipse converges into the target circular orbit.', 'Criterion: eccentricity relative to the Moon, e < 0.15.', 'The final speed is just the lunar circular speed v = √(GM_moon/r).'], 'range_note': 'Over-braking at perilune slams the other end into the surface; under-braking leaves a flat ellipse.', 'cases': [("Chang'e-1 orbit lowering", '12 h orbit → 3.5 h → 127 min circular, three braking burns in all.'), ('Lunar Orbiters / LRO', 'Entered big ellipses first, then lowered step by step to ~50 km polar mapping orbits.'), ('Apollo command module', 'Waited in a ~110 km circular lunar orbit for the ascent stage to return.')], 'trivia': "The Moon has no atmosphere, so there is no 'aerobraking' - every orbit lowering costs propellant."}]}, {'core': 'Make mechanical energy ≥ 0 - gravity can never catch up', 'body': ["Specific mechanical energy ε = v²/2 − μ/r is the yardstick for 'bound or not'.", 'ε < 0: tethered by gravity, tracing a closed ellipse that always returns.', 'ε ≥ 0: the path opens into a hyperbola, never to return.', 'Setting ε = 0 gives escape speed v = √(2μ/r) = √2 × circular speed.', 'At 200 km altitude that is ≈ 11.01 km/s; from the ground it is the textbook 11.2.', "Escape ≠ no gravity - gravity still pulls, it just can't pull you back."], 'range_note': 'Below escape speed you always come back, however far you fly; once above, altitude only grows.', 'cases': [('Tianwen-1 (2021)', 'Bound for Mars - it first had to exceed escape velocity to leave Earth.'), ('Lunar / Mars missions', 'All launch into escape or big transfer ellipses, then correct and brake later.'), ('Jupiter & Saturn deep-space probes', 'After leaving Earth they sling past planets for extra speed, saving huge amounts of fuel.')], 'trivia': 'Escape speed ignores mass: a ping-pong ball and a spaceship at the same height and speed follow the same path.'}, {'core': 'Escaping Earth is not enough - you must also escape the Sun', 'body': ['After leaving Earth, the spacecraft is still firmly held by the Sun.', 'But Earth runs around the Sun at 29.8 km/s, and that speed can be inherited.', "To escape the Sun from Earth's orbit, heliocentric speed needs √2 × 29.8 ≈ 42.1.", "Adding both accounts (beating Earth's gravity + the leftover heliocentric speed) gives about 16.7 from the ground.", 'That is the third cosmic velocity - not simply √2 times something.', 'In practice planetary gravity assists supply much of it, so no rocket carries it all.'], 'range_note': 'Below 16.7 km/s the Sun eventually traps the craft on some heliocentric ellipse - it never leaves the Solar System.', 'cases': [('Voyager 1 (launched 1977)', 'About 17 km/s relative to the Sun; entered interstellar space in 2012, the farthest human-made object.'), ('Voyager 2', 'About 15 km/s relative to the Sun; entered interstellar space in 2018, the only probe to visit Uranus and Neptune.'), ('Pioneers 10/11, New Horizons', 'Together with the two Voyagers, five probes are now leaving the Solar System.')], 'trivia': 'Gravity assist: sweeping behind a planet borrows its orbital momentum for almost no fuel.'}, {'core': 'Speed up to lift the far side, slow down to lower it; to circularize, burn again at the other apsis', 'body': ['Speed up: the burn point becomes the perigee and the opposite side rises - bigger, flatter orbit.', 'Slow down: the burn point becomes the apogee and the opposite side drops - smaller, flatter orbit.', 'One burn alone always leaves an ellipse, never a circle.', 'To circularize, fly to the other end and burn again, pulling the far side back.', 'Raising burns twice with speed; lowering burns twice against it - Hohmann transfer in both directions.', 'Higher circular orbits run slower: v = √(GM/r) - altitude sets the speed.'], 'range_note': "Too low and you can't get there; too high overshoots the target or flattens the orbit even more.", 'cases': [('BeiDou / GPS insertion', 'The rocket delivers the satellite into a transfer ellipse; the satellite circularizes itself at apogee.'), ('Station re-boosts', 'Cargo craft burn to offset the slow decay caused by thin residual atmosphere.'), ('Shenzhou re-entry', 'Retro-burn to lower the orbit until perigee dips into the atmosphere, then controlled re-entry.')], 'trivia': 'Slowing lowers an orbit and speeding raises it - it sounds backwards, because braking makes the orbit smaller.', 'phase_lesson': [{'core': 'Accelerate at perigee: this end stays, the apogee opposite is lifted', 'body': ["The burn point is always the new orbit's perigee: fastest here, so accelerating pays off most.", 'Vis-viva v = √(GM(2/r − 1/a)), with a = (perigee + apogee)/2.', 'Raising 200 km to 1200 km here needs about 8.05 km/s at perigee.', 'The orbit becomes a 200 km × 1200 km ellipse.', "Note: the spacecraft's altitude hasn't changed yet - only the orbit's shape has.", 'Next, fly to apogee and burn again to make this ellipse a circle.'], 'range_note': "Too slow and the apogee can't reach 1200 km; too fast overshoots, nearly escaping."}, {'core': "Top up speed at apogee to 'inflate' the ellipse into a circle", 'body': ['Apogee is the slowest point on the ellipse (about 6.99 km/s).', 'The circular speed there is 7.25 km/s - a little short.', "Adding that 0.26 km/s lifts the perigee up to the apogee's height → circle.", 'The criterion is eccentricity e < 0.05.', "This is the classic 'apogee circularization' of every GEO satellite insertion.", 'Two burns together beat one direct push - the essence of the Hohmann transfer.'], 'range_note': 'Too little and it stays an ellipse; too much lifts the perigee above the apogee and it flattens again.'}, {'core': 'Slow down in the high orbit: this end becomes apogee, the perigee opposite drops', 'body': ['Lowering is the exact mirror of raising - same math, opposite sign.', 'Retro-burn in the 1200 km circular orbit: this point instantly becomes the apogee.', 'Slow to about 7.02 km/s and the far side falls to 300 km.', 'The orbit becomes a 300 km × 1200 km ellipse.', "The spacecraft is still at 1200 km right now - it's the far side that changed.", 'Why does lowering enable return? This step pushes perigee into the atmosphere.'], 'range_note': "Too little and it won't come down; too much and perigee dives into the atmosphere - no coming back."}, {'core': "Slow again at perigee to 'shave' the ellipse into a circle", 'body': ['Perigee is the fastest point on the ellipse (about 7.96 km/s).', 'The 300 km circular orbit needs only 7.61 km/s - 0.35 too much.', "Shave that off and the apogee drops to the perigee's height → circle.", 'Check eccentricity e < 0.05 once more and the task is complete.', 'The craft now sits 100 km lower than it started - and runs faster.', "Remember: low orbits are fast, high orbits are slow (Kepler's third law)."], 'range_note': 'Too little and it stays an ellipse; too much drops the apogee below the perigee and squashes the orbit toward the atmosphere.'}]}]
current_task = 0
task_phase = 0
task_done = [False] * TASK_COUNT
auto_task = None
attempt_started = False
x = y = vx = vy = 0.0
sim_time = 0.0
moon_time = 0.0
paused = False
mission_started = False
collision_state = ''
msg = ''
trail_x = deque(maxlen=TRAIL_MAX_POINTS)
trail_y = deque(maxlen=TRAIL_MAX_POINTS)
history_states = deque(maxlen=1600)
predicted = [], [], [], [], []
predicted_t0 = 0.0
last_predict_wall = 0.0
preview_speed = None
preview_traj = [], []
preview_info = ''
pending_state = None
selecting_point = False
follow_view = True
show_labels = False
show_velocity = True
show_compare = False
show_force_analysis = False
comparison_traj = np.array([]), np.array([])
snapshots = []
simulation_rate = 1.0
toast_until = 0.0
toast_kind = 'info'
last_loop_wall = time.perf_counter()
last_gravity_sum = None
last_force_report = {}
_syncing_widget = False
_ui_rects = []
_group_rects = []

def circular_speed_at(radius):
    return float(np.sqrt(MU_EARTH / radius))

def escape_speed_at(radius):
    return float(np.sqrt(2 * MU_EARTH / radius))

def moon_circular_speed(radius):
    '''相对月球的圆轨道速度（km/s）。'''

    return float(np.sqrt(MU_MOON / max(float(radius), R_MOON)))

def moon_escape_speed(radius):
    return float(np.sqrt(2 * MU_MOON / max(float(radius), R_MOON)))

def transfer_speed(r_from, r_to):
    '''
    在半径 r_from 处沿切向点火，使轨道"另一端"的半径变成 r_to 所需的速度。

    这是霍曼转移的核心公式：a =（这一端 + 那一端）/ 2，再代活力公式。
    升轨、降轨、修圆全都用它 —— 让 r_to = r_from 就退化成圆轨道速度。
    '''

    r_from = max(float(r_from), R_EARTH)
    r_to = max(float(r_to), R_EARTH)
    a = (r_from + r_to) / 2
    return float(np.sqrt(max(MU_EARTH * (2 / r_from - 1 / a), 0.0)))

def moon_orbit_speed_for(r, r_target):
    '''月球版 transfer_speed：在距月心 r 的拱点点火，把另一端拉到 r_target。'''

    r = max(float(r), R_MOON + 5.0)
    r_target = max(float(r_target), R_MOON + 5.0)
    a = (r + r_target) / 2
    return float(np.sqrt(max(MU_MOON * (2 / r - 1 / a), 0.0)))

def moon_positions(times):
    '''矢量版月球位置：一次算出一批时刻的坐标，避免逐点调用拖慢界面。'''

    t = np.asarray(times, dtype=float)
    ang = MOON_INITIAL_ANGLE + MOON_ANGULAR_SPEED * t
    return np.column_stack([MOON_ORBIT_RADIUS * np.cos(ang), MOON_ORBIT_RADIUS * np.sin(ang)])

def moon_relative_elements(px=None, py=None, pvx=None, pvy=None, t=None):
    '''
    飞船相对月球的轨道根数。

    返回 (距月心 r, 相对速率 v, 比机械能 ε, 偏心率 e, 近月点半径, 远月点半径)。
    ε < 0 就是"被月球捕获"。
    '''

    px = x if px is None else px
    py = y if py is None else py
    pvx = vx if pvx is None else pvx
    pvy = vy if pvy is None else pvy
    t = moon_time if t is None else t
    mp, mv = moon_position(t)
    rel_p = np.array([float(px) - mp[0], float(py) - mp[1]], dtype=float)
    rel_v = np.array([float(pvx), float(pvy)], dtype=float) - np.asarray(mv, float)
    r = max(float(np.linalg.norm(rel_p)), R_MOON)
    v = float(np.linalg.norm(rel_v))
    energy = v * v / 2 - MU_MOON / r
    h = rel_p[0] * rel_v[1] - rel_p[1] * rel_v[0]
    ecc = float(np.sqrt(max(1 + 2 * energy * h * h / MU_MOON ** 2, 0.0)))
    if energy < 0:
        a = -MU_MOON / (2 * energy)
        peri, apo = a * (1 - ecc), a * (1 + ecc)
    else:
        peri, apo = r, np.inf
    return r, v, float(energy), ecc, float(peri), float(apo)

def moon_rel_speed():
    '''飞船相对月球的速率（km/s）。'''

    return float(moon_relative_elements()[1])

def moon_radial_velocity():
    '''相对月球的径向速度：>0 正在远离月球（近月点附近），<0 正在靠近。'''

    mp, mv = moon_position(moon_time)
    rel_p = np.array([x - mp[0], y - mp[1]], dtype=float)
    rel_v = np.array([vx, vy], dtype=float) - np.asarray(mv, dtype=float)
    r = max(float(np.linalg.norm(rel_p)), R_MOON)
    return float(np.dot(rel_p, rel_v)) / r

def burn_frame():
    '''
    点火与读数所用的参考系。

    "earth" = 地心惯性系（默认）；"moon" = 相对月球（任务 3 的近月制动 / 环月修圆）。
    换成月球系后，滑块、仪表盘、HUD 显示的都是"相对月球的速度"——
    这正是真实任务里近月制动用的量。

    判据用"距月球多远"而不是阶段号：阶段推进发生在点火之后，
    用它判断会让第一次制动落在错误的参考系上。
    '''

    if current_task != 2:
        return 'earth'
    mp, _ = moon_position(moon_time)
    dist = float(np.linalg.norm(np.array([x - mp[0], y - mp[1]])))
    if dist <= LUNAR_SOI_ENTER:
        return 'moon'
    return 'earth'

def current_speed():
    '''当前参考系下的速度：点火用的就是它。'''

    if burn_frame() == 'moon':
        return moon_rel_speed()
    return float(np.hypot(vx, vy))

def set_state(px, py, pvx, pvy, tsec):
    global x, y, vx, vy, sim_time, moon_time
    x, y, vx, vy = float(px), float(py), float(pvx), float(pvy)
    sim_time = float(tsec)
    moon_time = float(tsec)

def circular_orbit_state(altitude, angle=LAUNCH_ANGLE):
    r = R_EARTH + altitude
    vcirc = circular_speed_at(r)
    return r * np.cos(angle), r * np.sin(angle), -np.sin(angle) * vcirc, np.cos(angle) * vcirc

def initial_state_for_task(index):
    '''
    为每个任务准备起点轨道。任务 1 故意给一条 8.2 km/s 的椭圆轨道，
    学生必须减速才能修圆 —— 否则一开局就是标准答案，任务没有意义。
    '''

    if index == 0:
        px, py, tvx, tvy = circular_orbit_state(LAUNCH_ALTITUDE)
        return px, py, tvx * 8.2 / circular_speed_at(R_EARTH + LAUNCH_ALTITUDE), tvy * 8.2 / circular_speed_at(R_EARTH + LAUNCH_ALTITUDE), 0.0
    px, py, tvx, tvy = circular_orbit_state(LAUNCH_ALTITUDE)
    return px, py, tvx, tvy, 0.0

def reset_task(index=None, keep_view=True):
    '''切换/重置任务：回到该任务的起点轨道并清空轨迹。'''

    global current_task, task_phase, attempt_started, auto_task, mission_started, paused, collision_state, pending_state, selecting_point, preview_speed, trail_x, trail_y, history_states, comparison_traj
    if index is not None:
        current_task = index % TASK_COUNT
    task_phase = 0
    attempt_started = False
    auto_task = None
    mission_started = False
    paused = False
    collision_state = ''
    pending_state = None
    selecting_point = False
    preview_speed = None
    trail_x = deque(maxlen=TRAIL_MAX_POINTS)
    trail_y = deque(maxlen=TRAIL_MAX_POINTS)
    history_states = deque(maxlen=1600)
    comparison_traj = np.array([]), np.array([])
    set_state(*initial_state_for_task(current_task))
    trail_x.append(x)
    trail_y.append(y)
    history_states.append((x, y, vx, vy, moon_time))
    line_orbit.set_data(list(trail_x), list(trail_y))
    line_compare.set_data([], [])
    selected_marker.set_data([], [])
    rocket_point.set_data([x], [y])
    btn_pause.label.set_text(T('暂停'))
    btn_select_point.label.set_text(T('在轨迹上选点'))
    if not keep_view:
        reset_view()
    refresh_prediction(force=True)
    rocket_halo.set_center((x, y))
    update_moon_texture(moon_position(moon_time)[0])
    refresh_locators()
    refresh_force_analysis()
    sync_speed_widget()
    refresh_task_badges()
    refresh_card()
    refresh_hud()
    if fig.canvas is not None:
        fig.canvas.draw_idle()

def _declare_dpi_aware():
    if sys.platform != 'win32':
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        return

_declare_dpi_aware()
fig = plt.figure(figsize=(15.2, 9.3), facecolor=C_SPACE, dpi=100)
star_ax = fig.add_axes([0, 0, 1, 1], facecolor=C_SPACE, zorder=-5)
star_ax.set_axis_off()
_rng = np.random.default_rng(42)
star_ax.scatter(_rng.uniform(0, 1, 900), _rng.uniform(0, 1, 900), s=_rng.uniform(0.2, 2.2, 900), color='#dceaff', alpha=0.55, linewidths=0, zorder=0)

def canvas_px():
    '''
    当前画布像素尺寸；窗口尚未绘制时退回 figure 的名义尺寸。

    必须取**物理像素**：get_width_height() 默认返回"逻辑像素"，在系统缩放过的屏幕
    上它只有物理像素的 1/1.5（Tk 会把 fig.dpi 提到 150 再按屏幕缩放渲染）。而
    copy_from_bbox()/blit() 的区域、以及 event.x/event.y 用的都是物理像素，口径
    一旦不一致，刷新区域会缩到画面左下角一小块，其余大片区域永远停在首帧的画面上
    ——表现出来就是"视图区很小、外面一圈黑框"。
    '''

    try:
        w, h = fig.canvas.get_width_height(physical=True)
        if w < 2 or h < 2:
            raise ValueError
    except Exception:
        w, h = fig.get_size_inches() * fig.dpi
    return float(w), float(h)

def render_px():
    '''
    渲染坐标系里的画布尺寸（figure 像素）。

    copy_from_bbox()/blit() 认的是 figure 的渲染像素，平时与 canvas_px()（窗口物理
    像素）完全相等；只有窗口刚被最大化/拖动、Tk 还没把新尺寸回灌给 figure 的那一两
    帧里两者会差几十到几百像素。刷新区域一定要按渲染像素算 —— 否则那几帧会把画面
    贴到画布外面去，表现出来就是"四周一圈黑框、只有一角在动"。
    '''

    fb = fig.bbox
    return float(fb.width), float(fb.height)

_size_syncing = False

def sync_canvas_size():
    '''把 figure 的尺寸拉齐到窗口的物理像素，让画面立刻铺满、不留黑边。

    TkAgg 自己也会在 <Configure> 之后回灌尺寸，但那是"稍后"：启动最大化、F11 全屏、
    拖动窗口边缘时，中间总有一两帧是"窗口已经变大、figure 还是旧尺寸"，这一两帧的
    四周就是黑的。这里直接对齐，代价只有一次 set_size_inches。
    '''

    global _size_syncing
    if HEADLESS:
        return
    if _size_syncing:
        return
    w, h = canvas_px()
    cw, ch = render_px()
    if w < 2 or h < 2:
        return None
    if abs(w - cw) <= 2 and abs(h - ch) <= 2:
        return
    _size_syncing = True
    try:
        fig.set_size_inches(w / fig.dpi, h / fig.dpi, forward=False)
    finally:
        _size_syncing = False
    mark_ui_dirty()

def apply_view(cx, cy, span_x):
    '''以水平跨度 span_x 设定视野，中心为 (cx, cy)。'''

    span_x = float(np.clip(span_x, MIN_VIEW_SPAN, MAX_VIEW_SPAN))
    w, h = canvas_px()
    span_y = span_x * (h / max(w, 1.0))
    ax.set_xlim(cx - span_x / 2, cx + span_x / 2)
    ax.set_ylim(cy - span_y / 2, cy + span_y / 2)

def current_view():
    '''返回 (中心 x, 中心 y, 水平跨度)。'''

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0

def default_view():
    '''默认全景：竖直跨度容得下月球轨道，地球稍微偏上避开底部操作台。'''

    w, h = canvas_px()
    return 0.0, -HOME_UP_FRAC * HOME_SPAN_Y, HOME_SPAN_Y * (w / max(h, 1.0))

ax = fig.add_axes([0, 0, 1, 1], facecolor='none', zorder=0)
ax.set_axis_off()
apply_view(*default_view())
moon_orbit_ring = Circle((0, 0), MOON_ORBIT_RADIUS, fill=False, linestyle=(0, (3, 5)), linewidth=0.75, edgecolor='#5b6d80', alpha=0.7, zorder=1)
sync_orbit_ring = Circle((0, 0), SYNC_ORBIT_RADIUS, fill=False, linestyle=(0, (4, 5)), linewidth=0.9, edgecolor='#b49ad5', alpha=0.75, zorder=1)
near_orbit_ring = Circle((0, 0), NEAR_ORBIT_RADIUS, fill=False, linestyle=(0, (2, 4)), linewidth=0.8, edgecolor='#7fb5d6', alpha=0.85, zorder=1)
for _p in moon_orbit_ring, sync_orbit_ring, near_orbit_ring:
    ax.add_patch(_p)
_reg_text(ax.text(-MOON_ORBIT_RADIUS * 0.52, -MOON_ORBIT_RADIUS * 0.86, '', color='#8092a6', fontsize=8, rotation=34, zorder=2), '月球公转轨道')
_reg_text(ax.text(NEAR_ORBIT_RADIUS, 4000, '', color='#8dbbd8', fontsize=7.5, ha='left', va='bottom', zorder=2), '近地轨道')
_reg_text(ax.text(SYNC_ORBIT_RADIUS, 3000, '', color='#c0a9dc', fontsize=7.5, ha='left', va='bottom', zorder=2), '同步轨道')
earth_img, earth_src = load_texture('earth.png', 'earth')
moon_img, moon_src = load_texture('moon.png', 'moon')
earth_artist = ax.imshow(earth_img, extent=(-R_EARTH, R_EARTH, -R_EARTH, R_EARTH), interpolation='bilinear', zorder=2, aspect='auto')
moon_artist = ax.imshow(moon_img, extent=(0, 0, 0, 0), interpolation='bilinear', zorder=2, aspect='auto')
moon_marker = Circle((0, 0), 12000, fill=False, edgecolor=C_PURPLE, linewidth=1.2, alpha=0.95, zorder=3)
ax.add_patch(moon_marker)
earth_locator = Circle((0, 0), R_EARTH * 1.35, fill=False, edgecolor=C_BLUE, linewidth=1.1, alpha=0.85, zorder=3)
ax.add_patch(earth_locator)
earth_label = _reg_text(ax.text(0, 0, '地球', color=C_BLUE, fontsize=7.5, ha='center', va='center', zorder=3, visible=False), '地球')
moon_label = _reg_text(ax.text(0, 0, '月球', color=C_PURPLE, fontsize=7.5, ha='center', va='center', zorder=3), '月球')
rocket_halo = Circle((0, 0), 9500, color=C_AMBER, alpha=0.18, zorder=4)
ax.add_patch(rocket_halo)

def refresh_locators():
    '''让地球/月球的定位标记随视野大小变化，缩再远也找得到。'''

    _, _, span_x = current_view()
    rad = max(R_EARTH * 1.35, span_x * 0.014)
    earth_locator.set_radius(rad)
    rocket_halo.set_radius(float(np.clip(span_x * 0.01, 320.0, 9500.0)))
    mp = moon_position(moon_time)[0]
    moon_label.set_position((mp[0], mp[1] - max(span_x * 0.026, R_MOON * MOON_TEXTURE_SCALE * 2.2)))
    earth_label.set_position((0, -rad - span_x * 0.022))
    earth_label.set_visible(span_x > 8 * R_EARTH)

def update_moon_texture(position):
    rad = R_MOON * MOON_TEXTURE_SCALE
    moon_artist.set_extent((position[0] - rad, position[0] + rad, position[1] - rad, position[1] + rad))
    moon_marker.set_center(tuple(position))

update_moon_texture(moon_position(0)[0])
refresh_locators()
(line_compare,) = ax.plot([], [], color='#9fb0c2', lw=1.0, alpha=0.4, linestyle=':', zorder=2.6)
(line_predict,) = ax.plot([], [], color='#8f9aa8', lw=0.9, alpha=0.75, linestyle='--', zorder=2.8)
(line_preview,) = ax.plot([], [], color=C_CYAN, lw=1.3, alpha=0.95, linestyle='--', zorder=3.2)
(line_orbit,) = ax.plot([], [], color=C_TRAIL, lw=1.25, alpha=0.55, zorder=3)
(line_recent,) = ax.plot([], [], color='#ff9c6b', lw=1.7, zorder=3.1)
(rocket_point,) = ax.plot([], [], marker='o', color='#fff0b8', markersize=5.0, markeredgecolor='#ff9d2e', zorder=9)
(selected_marker,) = ax.plot([], [], marker='D', color='#ffe27a', markeredgecolor='#ffffff', markersize=8, linestyle='None', zorder=10)
(guide_marker,) = ax.plot([], [], marker='*', color=C_GREEN, markeredgecolor='#ffffff', markersize=15, linestyle='None', zorder=10)
vec_vel = FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=12, color=C_GREEN, linewidth=1.6, zorder=8)
ax.add_patch(vec_vel)
grav_arrow_earth = FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=11, color=C_BLUE, linewidth=1.5, zorder=7.6, visible=False)
grav_arrow_moon = FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=11, color=C_PURPLE, linewidth=1.5, zorder=7.6, visible=False)
grav_arrow_sum = FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=13, color='#ffffff', linewidth=1.9, alpha=0.92, zorder=7.8, visible=False)
grav_arrow_tan = FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=9, color=C_AMBER, linewidth=1.3, linestyle='--', zorder=7.7, visible=False)
grav_arrow_norm = FancyArrowPatch((0, 0), (0, 0), arrowstyle='-|>', mutation_scale=9, color=C_CYAN, linewidth=1.3, linestyle='--', zorder=7.7, visible=False)
grav_text_earth = _reg_text(ax.text(0, 0, '地球引力', color=C_BLUE, fontsize=7.5, ha='center', va='center', zorder=8.2, visible=False), '地球引力')
grav_text_moon = _reg_text(ax.text(0, 0, '月球引力', color=C_PURPLE, fontsize=7.5, ha='center', va='center', zorder=8.2, visible=False), '月球引力')
grav_text_tan = _reg_text(ax.text(0, 0, '切向', color=C_AMBER, fontsize=7.0, ha='center', va='center', zorder=8.2, visible=False), '切向')
grav_text_norm = _reg_text(ax.text(0, 0, '法向', color=C_CYAN, fontsize=7.0, ha='center', va='center', zorder=8.2, visible=False), '法向')
for _a in grav_arrow_earth, grav_arrow_moon, grav_arrow_sum, grav_arrow_tan, grav_arrow_norm:
    ax.add_patch(_a)
force_panel_bg = FancyBboxPatch((FORCE_PANEL_X, FORCE_PANEL_Y), FORCE_PANEL_W, FORCE_PANEL_H, boxstyle='round,pad=0.004,rounding_size=0.014', transform=ax.transAxes, fc='#08111c', ec=C_AMBER, lw=1.0, alpha=0.9, zorder=13, visible=False)
ax.add_patch(force_panel_bg)
force_panel_lines = []
for _i in range(FORCE_PANEL_ROWS):
    _t = ax.text(FORCE_PANEL_X + 0.013, FORCE_PANEL_Y + FORCE_PANEL_H - 0.021 - _i * FORCE_LINE_H, '', transform=ax.transAxes, ha='left', va='center', fontsize=8, color=C_TEXT, zorder=14, visible=False)
    force_panel_lines.append(_t)
peri_label = _reg_text(ax.text(0, 0, '近地点', color=C_AMBER, fontsize=8.5, ha='center', va='bottom', visible=False, zorder=10, bbox=dict(boxstyle='round,pad=0.18', fc='#0d1521', ec=C_AMBER, lw=0.6, alpha=0.85)), '近地点')
apo_label = _reg_text(ax.text(0, 0, '远地点', color=C_AMBER, fontsize=8.5, ha='center', va='top', visible=False, zorder=10, bbox=dict(boxstyle='round,pad=0.18', fc='#0d1521', ec=C_AMBER, lw=0.6, alpha=0.85)), '远地点')
hud_text = ax.text(0.012, 0.922, '', transform=ax.transAxes, ha='left', va='top', color=C_TEXT, fontsize=9.5, zorder=12, bbox=dict(boxstyle='round,pad=0.4', fc='#08111c', ec=C_EDGE, lw=0.8, alpha=0.82))
toast_patch = FancyBboxPatch((0.028, 0.665), 0.52, 0.105, boxstyle='round,pad=0.006,rounding_size=0.03', transform=ax.transAxes, fc='#10233a', ec=C_BLUE, lw=1.2, alpha=0.94, zorder=14, visible=False)
ax.add_patch(toast_patch)
toast_text = ax.text(0.288, 0.717, '', transform=ax.transAxes, ha='center', va='center', color=C_TEXT, fontsize=10.5, zorder=15, visible=False, wrap=True)
title_ax = fig.add_axes([0, 0.945, 1, 0.055], facecolor=C_PANEL, zorder=5)
title_ax.set_axis_off()
title_ax.patch.set_alpha(0.82)
_reg_text(title_ax.text(0.035, 0.52, '', transform=title_ax.transAxes, ha='left', va='center', color=C_TEXT, fontsize=13, weight='bold'), '宇宙速度探究器')
_reg_text(title_ax.text(0.14, 0.52, '', transform=title_ax.transAxes, ha='left', va='center', color=C_DIM, fontsize=8.5), '拖速度滑块 → 看虚线 → 点火')
task_buttons = []
_badge_x = 0.3
for i in range(TASK_COUNT):
    bax = fig.add_axes([_badge_x + i * 0.062, 0.9525, 0.056, 0.04], zorder=8)
    btn = Button(bax, f'{TASK_ICONS[i]} {T(TASK_SHORT[i])}', color='#1a2734', hovercolor='#1f4f73')
    btn.label.set_color(C_DIM)
    btn.label.set_fontsize(8)
    btn.on_clicked((lambda ev, idx=i: select_task(idx)))
    task_buttons.append(btn)
ax_lang = fig.add_axes([0.674, 0.9525, 0.048, 0.04], zorder=8)
btn_lang = Button(ax_lang, 'EN' if UI_LANG == 'zh' else '中文', color='#1a2734', hovercolor='#2f6f9e')
btn_lang.label.set_color(C_DIM)
btn_lang.label.set_fontsize(8)
btn_lang.on_clicked((lambda ev: set_ui_language('en' if UI_LANG == 'zh' else 'zh')))
ax_immersive = fig.add_axes([0.728, 0.9525, 0.056, 0.04], zorder=8)
btn_immersive = Button(ax_immersive, T('沉浸 V'), color='#1a2734', hovercolor='#2f6f9e')
btn_immersive.label.set_color(C_DIM)
btn_immersive.label.set_fontsize(8)
btn_immersive.on_clicked((lambda ev: toggle_immersive()))
ax_force = fig.add_axes([0.79, 0.9525, 0.098, 0.04], zorder=8)
btn_force = Button(ax_force, T('受力分析 F'), color='#1a2734', hovercolor='#2f6f9e')
_reg_text(btn_force.label, '受力分析 F')
btn_force.label.set_color(C_DIM)
btn_force.label.set_fontsize(8)
btn_force.on_clicked((lambda ev: toggle_force_analysis()))
ax_pause = fig.add_axes([0.894, 0.9525, 0.048, 0.04], zorder=8)
btn_pause = Button(ax_pause, T('暂停'), color='#1a2734', hovercolor='#3d4f61')
btn_pause.label.set_color(C_TEXT)
btn_pause.label.set_fontsize(8.5)
btn_pause.on_clicked((lambda ev: toggle_pause()))
ax_reset = fig.add_axes([0.947, 0.9525, 0.05, 0.04], zorder=8)
btn_reset = Button(ax_reset, T('重新发射'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_reset.label, '重新发射')
btn_reset.label.set_color(C_TEXT)
btn_reset.label.set_fontsize(8)
btn_reset.on_clicked((lambda ev: reset_task(None, keep_view=True)))
card_ax = fig.add_axes([0.655, 0.345, 0.31, 0.585], facecolor=C_PANEL, zorder=5)
card_ax.set_xticks([])
card_ax.set_yticks([])
card_ax.patch.set_alpha(0.94)
for sp in card_ax.spines.values():
    sp.set_color(C_EDGE)
    sp.set_linewidth(1.1)
card_page = 0
_card_groups = [], []

def card_text(y, size=8.5, color=C_TEXT, weight='normal', page=0, content=''):
    artist = card_ax.text(0.055, y, content, transform=card_ax.transAxes, ha='left', va='top', fontsize=size, color=color, weight=weight, wrap=True)
    _card_groups[page].append(artist)
    return artist

def card_rule(y, page=0):
    lines = card_ax.plot([0.05, 0.95], [y, y], transform=card_ax.transAxes, color=C_EDGE, lw=0.8, clip_on=False)
    for line in lines:
        _card_groups[page].append(line)
    return lines

card_tab_buttons = []
for _tx, _label, _page in ((0.662, '① 任务与操作', 0), (0.817, '② 原理与案例', 1)):
    _tax = fig.add_axes([_tx, 0.884, 0.148, 0.04], zorder=9)
    _tab = Button(_tax, T(_label), color='#1a2734', hovercolor='#2f6f9e')
    _reg_text(_tab.label, _label)
    _tab.label.set_color(C_DIM)
    _tab.label.set_fontsize(8)
    _tab.on_clicked((lambda ev, p=_page: switch_card_page(p)))
    card_tab_buttons.append(_tab)
card_no = card_text(0.898, 8.5, C_DIM)
card_name = card_text(0.855, 14, C_CYAN, 'bold')
card_goal = card_text(0.79, 8.5, C_TEXT)
card_rule(0.745)
_reg_text(card_text(0.716, 9, C_AMBER, 'bold', content='达成条件'), '达成条件')
check_lines = [card_text(0.668 - i * 0.05, 8.5, C_DIM) for i in range(4)]
card_rule(0.478)
_reg_text(card_text(0.45, 9, C_AMBER, 'bold', content='操作提示'), '操作提示')
guide_point = card_text(0.408, 8.5, C_TEXT)
guide_speed = card_text(0.356, 9.5, C_GREEN, 'bold')
guide_hint = card_text(0.288, 8, C_DIM)
card_peek = card_text(0.222, 8, C_PURPLE)
card_rule(0.18)
_reg_text(card_text(0.153, 9, C_AMBER, 'bold', content='实时飞行数据'), '实时飞行数据')
data_lines = [card_text(0.118 - i * 0.042, 8.5, C_TEXT) for i in range(3)]
lesson_tag = card_text(0.9, 8.5, C_DIM, page=1)
lesson_core = card_text(0.858, 12, C_CYAN, 'bold', page=1)
card_rule(0.826, page=1)
lesson_body = [card_text(0.796 - i * 0.042, 8, C_TEXT, page=1) for i in range(6)]
card_rule(0.556, page=1)
_reg_text(card_text(0.528, 9, C_AMBER, 'bold', page=1, content='合理速度范围（当前位置）'), '合理速度范围（当前位置）')
range_value = card_text(0.482, 13, C_GREEN, 'bold', page=1)
range_note = card_text(0.436, 7.5, C_DIM, page=1)
range_judge = card_text(0.368, 8, C_AMBER, page=1)
card_rule(0.336, page=1)
_reg_text(card_text(0.308, 9, C_AMBER, 'bold', page=1, content='现实中的航天任务'), '现实中的航天任务')
case_names = [card_text(0.276 - i * 0.074, 8.5, C_TEXT, 'bold', page=1) for i in range(3)]
case_details = [card_text(0.248 - i * 0.074, 7.5, C_DIM, page=1) for i in range(3)]
card_rule(0.07, page=1)
trivia_head = card_text(0.044, 7.5, C_PURPLE, page=1)
panel_ax = fig.add_axes([0, 0, 1, 0.345], facecolor='none', zorder=4)
panel_ax.set_axis_off()

def group_box(rx, ry, rw, rh, title, color=C_BLUE):
    '''分组框：坐标全部使用 figure 归一化坐标，与 add_axes 一致，避免换算错误。'''

    panel_ax.add_patch(FancyBboxPatch((rx, ry), rw, rh, boxstyle='round,pad=0.003,rounding_size=0.018', transform=fig.transFigure, fc=C_PANEL, alpha=0.86, ec=C_EDGE, lw=1.0, zorder=1))
    _group_rects.append((rx, ry, rx + rw, ry + rh))
    _reg_text(fig.text(rx + 0.014, ry + rh - 0.024, '', ha='left', va='center', fontsize=9.5, color=color, weight='bold', zorder=6), title)
    from matplotlib.lines import Line2D
    fig.add_artist(Line2D([rx + 0.004, rx + rw - 0.004], [ry + rh - 0.042, ry + rh - 0.042], transform=fig.transFigure, color=C_EDGE, lw=0.8, alpha=0.9, zorder=6))

group_box(0.035, 0.055, 0.31, 0.25, '① 调速度', C_AMBER)
group_box(0.365, 0.055, 0.25, 0.25, '② 点火与演示', C_RED)
group_box(0.645, 0.055, 0.32, 0.25, '③ 观察工具', C_BLUE)
gauge_ax = fig.add_axes([0.048, 0.216, 0.283, 0.042], facecolor='#0a1622', zorder=8)
gauge_ax.set_xlim(0, SPEED_SLIDER_MAX)
gauge_ax.set_ylim(0, 1)
gauge_ax.set_xticks([])
gauge_ax.set_yticks([])
for sp in gauge_ax.spines.values():
    sp.set_color(C_EDGE)
    sp.set_linewidth(0.8)
gauge_ax.axvspan(0, V1, color='#1c3f60', alpha=0.95)
gauge_ax.axvspan(V1, V2, color='#1f6f7a', alpha=0.95)
gauge_ax.axvspan(V2, V3, color='#a8632c', alpha=0.95)
gauge_ax.axvspan(V3, SPEED_SLIDER_MAX, color='#8f2f38', alpha=0.95)
for v in V1, V2, V3:
    gauge_ax.axvline(v, color='#ffffff', lw=0.9, alpha=0.9)
(gauge_cursor,) = gauge_ax.plot([0, 0], [0, 1], color='#ffffff', lw=2.0, zorder=5)
(gauge_cursor_head,) = gauge_ax.plot([0], [0.92], marker='v', color='#ffffff', markersize=7, zorder=6)
(gauge_preview_head,) = gauge_ax.plot([], [], marker='^', color=C_AMBER, markersize=8, zorder=7)
target_band = Rectangle((0, -0.05), 0, 1.1, facecolor=C_GREEN, alpha=0.28, edgecolor=C_GREEN, lw=1.3, zorder=4)
gauge_ax.add_patch(target_band)
_reg_text(panel_ax.text(0.048, 0.208, '', transform=fig.transFigure, ha='left', va='top', fontsize=7.5, color=C_DIM, zorder=10), '速度参考线：7.9 环绕地球   11.2 脱离地球   16.7 飞出太阳系')
target_range_text = panel_ax.text(0.048, 0.184, '', transform=fig.transFigure, ha='left', va='top', fontsize=7.5, color=C_GREEN, zorder=10)

def refresh_target_band():
    '''把当前任务的合理速度区间画成仪表盘上的绿带。'''

    try:
        lower, upper, best, _ = current_target_range()
    except Exception:
        pass
    else:
        top = SPEED_SLIDER_MAX if upper is None else upper
        left = float(np.clip(lower, 0, SPEED_SLIDER_MAX))
        target_band.set_x(left)
        target_band.set_width(max(float(top) - left, 0.0))
        rng_txt = f'{left:.2f}' + ('' if upper is None else f' ~ {upper:.2f}')
        unit = T('（相对月球）') if burn_frame() == 'moon' else ''
        target_range_text.set_text(T('绿色 = 本任务合理区间 {a} {b}').format(a=rng_txt, b='km/s' + unit if unit else 'km/s'))

ax_slider = fig.add_axes([0.048, 0.13, 0.283, 0.034], facecolor=C_PANEL2, zorder=8)
speed_slider = Slider(ax_slider, '', SLIDER_MIN_SPEED, SPEED_SLIDER_MAX, valinit=V1, valstep=0.01, color=C_AMBER, track_color='#0a1622')
speed_slider.valtext.set_color(C_AMBER)
speed_slider.valtext.set_fontsize(9)
speed_slider.valtext.set_text(f'{V1:.2f} km/s')
ax_speed_box = fig.add_axes([0.048, 0.072, 0.085, 0.042], zorder=8)
speed_input = TextBox(ax_speed_box, '', initial=f'{V1:.2f}', color='#0a1622', hovercolor='#142434', label_pad=0.02, textalignment='center')
speed_input.text_disp.set_color('#ffffff')
speed_input.text_disp.set_fontsize(10)
ax_fill = fig.add_axes([0.145, 0.072, 0.108, 0.042], zorder=8)
btn_fill = Button(ax_fill, T('用推荐速度'), color='#1d4f45', hovercolor='#2a7462')
_reg_text(btn_fill.label, '用推荐速度')
btn_fill.label.set_color('#ffffff')
btn_fill.label.set_fontsize(8)
btn_fill.on_clicked((lambda ev: fill_recommended_speed()))
ax_clear = fig.add_axes([0.263, 0.072, 0.068, 0.042], zorder=8)
btn_clear = Button(ax_clear, T('清除预览'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_clear.label, '清除预览')
btn_clear.label.set_color(C_DIM)
btn_clear.label.set_fontsize(8)
btn_clear.on_clicked((lambda ev: clear_preview()))
preview_text = panel_ax.text(0.048, 0.038, T('拖动滑块：亮青色虚线就是「如果现在点火」的轨道'), transform=fig.transFigure, ha='left', va='center', fontsize=8, color=C_CYAN, zorder=10)
ax_fire = fig.add_axes([0.378, 0.196, 0.222, 0.052], zorder=8)
btn_fire = Button(ax_fire, T('点 火（按 Enter）'), color='#a8372f', hovercolor='#d4473a')
btn_fire.label.set_color('#ffffff')
btn_fire.label.set_fontsize(10.5)
btn_fire.label.set_weight('bold')
btn_fire.on_clicked((lambda ev: fire()))
ax_select = fig.add_axes([0.378, 0.128, 0.106, 0.044], zorder=8)
btn_select_point = Button(ax_select, T('在轨迹上选点'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_select_point.label, '在轨迹上选点')
btn_select_point.label.set_color(C_TEXT)
btn_select_point.label.set_fontsize(8)
btn_select_point.on_clicked((lambda ev: toggle_point_selection()))
ax_jump = fig.add_axes([0.494, 0.128, 0.106, 0.044], zorder=8)
btn_jump = Button(ax_jump, T('跳到推荐点'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_jump.label, '跳到推荐点')
btn_jump.label.set_color(C_TEXT)
btn_jump.label.set_fontsize(8)
btn_jump.on_clicked((lambda ev: jump_to_recommended()))
ax_demo = fig.add_axes([0.378, 0.066, 0.106, 0.044], zorder=8)
btn_demo = Button(ax_demo, T('自动演示'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_demo.label, '自动演示')
btn_demo.label.set_color(C_TEXT)
btn_demo.label.set_fontsize(8)
btn_demo.on_clicked((lambda ev: run_auto_demo()))
ax_home = fig.add_axes([0.494, 0.066, 0.106, 0.044], zorder=8)
btn_home = Button(ax_home, T('复位视角'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_home.label, '复位视角')
btn_home.label.set_color(C_TEXT)
btn_home.label.set_fontsize(8)
btn_home.on_clicked((lambda ev: reset_view()))
_reg_text(panel_ax.text(0.378, 0.026, '', transform=fig.transFigure, ha='left', va='center', fontsize=7.5, color=C_DIM, zorder=10), '空格=暂停    Enter=点火    R=重来    H=讲解    F=受力分析    滚轮=缩放    拖动画面=平移')
ax_checks = fig.add_axes([0.658, 0.128, 0.152, 0.132], facecolor=C_PANEL2, zorder=8)
ax_checks.patch.set_alpha(0.9)
OBS_TOGGLES = ('近/远地点标注', '速度箭头', '点火前对比', '视角跟随')
check = CheckButtons(ax_checks, [T(x) for x in OBS_TOGGLES], [False, True, False, True])
for lbl, zh in zip(check.labels, OBS_TOGGLES):
    _LANG_ARTISTS.append((lbl, zh))
    lbl.set_color(C_TEXT)
    lbl.set_fontsize(7.5)
check.on_clicked((lambda label: on_observation_toggle(label)))
ax_snap = fig.add_axes([0.658, 0.092, 0.152, 0.032], zorder=8)
btn_snap = Button(ax_snap, T('保存轨道快照'), color='#1a2734', hovercolor='#3d4f61')
_reg_text(btn_snap.label, '保存轨道快照')
btn_snap.label.set_color(C_TEXT)
btn_snap.label.set_fontsize(7.5)
btn_snap.on_clicked((lambda ev: capture_snapshot()))
ax_rate = fig.add_axes([0.825, 0.158, 0.135, 0.032], facecolor=C_PANEL2, zorder=8)
rate_slider = Slider(ax_rate, '', RATE_MIN, RATE_MAX, valinit=simulation_rate, valstep=RATE_STEP, color=C_BLUE, track_color='#0a1622')
_reg_text(panel_ax.text(0.825, 0.2, '', transform=fig.transFigure, ha='left', va='top', fontsize=8, color=C_DIM, zorder=10), '仿真倍速（最高 16×）')
rate_slider.valtext.set_position((0.97, 0.5))
rate_slider.valtext.set_ha('right')
rate_slider.valtext.set_color('#ffffff')
rate_slider.valtext.set_fontsize(8)
rate_slider.valtext.set_text(f'{simulation_rate:g}×')
rate_slider.on_changed((lambda v: on_rate_change(v)))
rate_preset_buttons = []
for i, _preset in enumerate(RATE_PRESETS):
    _bx = fig.add_axes([0.825 + i * 0.0342, 0.108, 0.031, 0.032], zorder=8)
    _btn = Button(_bx, f'{_preset:g}×', color='#1a2734', hovercolor='#2f6f9e')
    _btn.label.set_color(C_TEXT)
    _btn.label.set_fontsize(6.5)
    _btn.on_clicked((lambda ev, v=_preset: set_simulation_rate(v)))
    rate_preset_buttons.append(_btn)
snapshot_axes = []
for i, sx in enumerate((0.658, 0.75, 0.842)):
    pax = fig.add_axes([sx, 0.056, 0.082, 0.03], facecolor='#0a1622', zorder=8)
    pax.set_xticks([])
    pax.set_yticks([])
    for sp in pax.spines.values():
        sp.set_color(C_EDGE)
        sp.set_linewidth(0.6)
    pax.text(0.5, 0.5, T('空'), ha='center', va='center', fontsize=7, color='#3d5266', transform=pax.transAxes)
    snapshot_axes.append(pax)
immersive = False
_UI_AXES = [a for a in fig.axes if a is not star_ax if a is not ax if a is not ax_immersive]
_UI_EXTRA = list(fig.texts) + list(fig.artists)

def set_immersive(on):
    '''
    沉浸模式开关：收起标题栏、右侧引导卡、底部操作台，只留宇宙、HUD 与提示条。

    隐藏用 ax.set_visible(False) 而不是挪走坐标 —— matplotlib 的 canvas.inaxes()
    会跳过隐藏的 axes，控件因此自动失效，不会出现"看不见但点得到"的幽灵按钮。
    '''

    global immersive
    on = bool(on)
    if on == immersive and title_ax.get_visible() == (not on):
        return
    immersive = on
    for _ax in _UI_AXES:
        _ax.set_visible(not on)
    for art in _UI_EXTRA:
        art.set_visible(not on)
    try:
        btn_immersive.label.set_text(T('沉浸 √' if on else '沉浸 V'))
    except Exception:
        pass
    rebuild_ui_rects()
    mark_ui_dirty()
    fig.canvas.draw_idle()
    if on:
        toast(T('沉浸模式：面板已收起，滚轮缩放 / 按住左键拖动平移 / 按 V 或 Esc 退出'), 5.0, 'info')

def toggle_immersive():
    set_immersive(not immersive)

TOAST_COLORS = {'info': C_BLUE, 'success': C_GREEN, 'warn': C_AMBER, 'error': C_RED}

def toast(message, seconds=3.2, kind='info'):
    global toast_until, toast_kind
    toast_text.set_text(message)
    toast_text.set_visible(True)
    toast_patch.set_visible(True)
    toast_patch.set_edgecolor(TOAST_COLORS.get(kind, C_BLUE))
    toast_patch.set_facecolor({'info': '#10233a', 'success': '#0f2e22', 'warn': '#33270f', 'error': '#331417'}.get(kind, '#10233a'))
    toast_until = time.perf_counter() + seconds
    toast_kind = kind

def update_toast():
    if toast_until:
        if time.perf_counter() > toast_until:
            toast_patch.set_visible(False)
            toast_text.set_visible(False)

def pan_towards(cx, cy, ease=0.18):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    half_w = (x1 - x0) / 2
    half_h = (y1 - y0) / 2
    tx, ty = (x0 + x1) / 2, (y0 + y1) / 2
    ax.set_xlim(tx + (cx - tx) * ease - half_w, tx + (cx - tx) * ease + half_w)
    ax.set_ylim(ty + (cy - ty) * ease - half_h, ty + (cy - ty) * ease + half_h)

def zoom_view(factor, focus_x=None, focus_y=None):
    '''以 (focus_x, focus_y) 为焦点缩放；两个方向同比例，圆不会被拉扁。'''

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    cx, cy, span_x = current_view()
    if focus_x is None or focus_y is None:
        focus_x, focus_y = cx, cy
    new_span = float(np.clip(span_x * factor, MIN_VIEW_SPAN, MAX_VIEW_SPAN))
    k = new_span / max(span_x, 1e-9)
    if abs(k - 1.0) < 1e-9:
        return
    ax.set_xlim(focus_x - (focus_x - x0) * k, focus_x + (x1 - focus_x) * k)
    ax.set_ylim(focus_y - (focus_y - y0) * k, focus_y + (y1 - focus_y) * k)

def pan_view(dx_data, dy_data):
    '''按数据坐标平移视野（拖拽用）。'''

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 + dx_data, x1 + dx_data)
    ax.set_ylim(y0 + dy_data, y1 + dy_data)

def reset_view(event=None):
    apply_view(*default_view())
    refresh_orbit_annotations()
    refresh_locators()
    toast(T('视角已复位：可以看到完整的地月尺度（拖动画面还能平移）'), 2.6)
    fig.canvas.draw_idle()

def sync_view_aspect():
    '''窗口尺寸变化后按新的宽高比重算竖直跨度，保证 1 km 横竖一样长。'''

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    w, h = canvas_px()
    span_y = (x1 - x0) * (h / max(w, 1.0))
    cy = (y0 + y1) / 2
    ax.set_ylim(cy - span_y / 2, cy + span_y / 2)

def follow_target_if_needed():
    '''视角跟随：飞船接近画面边缘时平滑回中，避免"飞船不见了"。'''

    if not follow_view or dragging:
        return None
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    fx = (x - x0) / (x1 - x0)
    fy = (y - y0) / (y1 - y0)
    if 0.22 < fx < 0.78 and 0.22 < fy < 0.78:
        return
    pan_towards(x, y, ease=0.22)

def peri_apo_now():
    return apoapsis_periapsis(x, y, vx, vy)

def predicted_apsis_state(high=True):
    '''在预测轨迹上找远地点(True) / 近地点(False)的完整状态，找不到就返回 None。'''

    if not len(predicted[0]):
        return
    radii = np.hypot(predicted[0], predicted[1])
    i = int(np.argmax(radii)) if high else int(np.argmin(radii))
    return float(predicted[0][i]), float(predicted[1][i]), float(predicted[2][i]), float(predicted[3][i]), float(predicted[4][i])

def predicted_moon_extreme(high=True):
    '''
    在预测轨迹上找距月球最远 / 最近的那一点。

    返回 (状态, 该点距月心半径)；掠月时"最近点"就是飞掠近月点，
    已被捕获时它俩分别是环月轨道的近月点与远月点 —— 正是应该点火的地方。
    '''

    if not len(predicted[0]):
        return (None, None)
    mp = moon_positions(predicted[4])
    d = np.hypot(predicted[0] - mp[:, 0], predicted[1] - mp[:, 1])
    i = int(np.argmax(d)) if high else int(np.argmin(d))
    st = float(predicted[0][i]), float(predicted[1][i]), float(predicted[2][i]), float(predicted[3][i]), float(predicted[4][i])
    return st, float(d[i])

def task_checklist():
    '''返回 [(标题, 是否达成, 实时数值说明)]。'''

    peri, apo, energy, ecc = peri_apo_now()
    speed = float(np.hypot(vx, vy))
    items = []
    if current_task == 0:
        items.append((T('轨道是圆（偏心率 < 0.05）'), ecc < 0.05, f'e = {ecc:.3f}'))
        items.append((T('近地点高度在 150~1500 km'), R_EARTH + 150 < peri < R_EARTH + 1500, f'{peri - R_EARTH:,.0f} km'))
        return items
    if current_task == 1:
        items.append((T('第 1 步：远地点升到同步轨道附近'), task_phase >= 1, T('远地点 {a:,.0f} km（目标约 {b:,.0f}）').format(a=apo, b=SYNC_ORBIT_RADIUS)))
        items.append((T('第 2 步：在远地点把椭圆修圆（e < 0.05）'), task_phase >= 1 and ecc < 0.05, f'e = {ecc:.3f}'))
        items.append((T('半长轴落在同步轨道 ±3%'), np.isfinite(apo) and 0.97 * SYNC_ORBIT_RADIUS <= (peri + apo) / 2 <= 1.03 * SYNC_ORBIT_RADIUS, f'{(peri + apo) / 2:,.0f} km'))
        return items
    if current_task == 2:
        moon_pos, _ = moon_position(moon_time)
        gap = abs(apo - MOON_ORBIT_RADIUS)
        items.append((T('转移：远地点到月球轨道 ±20%'), task_phase >= 1 or 0.8 * MOON_ORBIT_RADIUS <= apo <= 1.2 * MOON_ORBIT_RADIUS, T('远地点 {a:,.0f} km，差 {b:,.0f} km').format(a=apo, b=gap)))
        r_rel, v_rel, e_rel, ecc_rel, peri_r, apo_r = moon_relative_elements()
        captured = e_rel < 0 and r_rel < MOON_SOI_RADIUS
        items.append((T('近月制动：被月球捕获（相对月球 ε<0）'), captured, T('相对月球 {a:.2f} / 逃逸 {b:.2f} km/s').format(a=v_rel, b=moon_escape_speed(r_rel))))
        peri_alt = peri_r - R_MOON
        items.append((T('不撞月：近月点高度 > 100 km'), captured and peri_alt > 100, T('近月点 {a:,.0f} km').format(a=peri_alt) if captured else T('还没被捕获')))
        items.append((T('修成环月圆轨道（相对月球 e < 0.15）'), captured and ecc_rel < 0.15, f'e = {ecc_rel:.3f}' if captured else T('还没被捕获')))
        return items
    if current_task == 5:
        items.append((T('① 升轨：远地点抬到 1200 km'), task_phase >= 1, T('√ 已完成') if task_phase >= 1 else T('远地点 {a:,.0f} km').format(a=apo - R_EARTH)))
        items.append((T('② 修圆：1200 km 圆轨道（e<0.05）'), task_phase >= 2, T('√ 已完成') if task_phase >= 2 else f'e = {ecc:.3f}'))
        items.append((T('③ 降轨：近地点降到 300 km'), task_phase >= 3, T('√ 已完成') if task_phase >= 3 else T('近地点 {a:,.0f} km').format(a=peri - R_EARTH)))
        a_now = (peri + apo) / 2
        items.append((T('④ 修圆：300 km 圆轨道（e<0.05）'), task_phase >= 3 and ecc < 0.05 and abs(a_now - LOW_ORBIT_R) <= 0.03 * LOW_ORBIT_R, f'e = {ecc:.3f}  a = {a_now:,.0f} km'))
        return items
    if current_task == 3:
        items.append((T('机械能 ≥ 0（不再被地球束缚）'), energy >= 0, f'ε = {energy:.3f}'))
        items.append((T('速度超过逃逸速度'), speed >= escape_speed_at(np.hypot(x, y)), f'{speed:.2f} km/s'))
        return items
    items.append((T('速度 ≥ 16.7 km/s'), speed >= V3, f'{speed:.2f} km/s'))
    items.append((T('已经脱离地球引力'), energy >= 0, f'ε = {energy:.3f}'))
    return items

def task_is_complete():
    if not attempt_started:
        return False
    return all(item[1] for item in task_checklist())

def recommended_state():
    '''当前任务推荐的点火点（含时间）与推荐速度。'''

    if current_task == 2 and task_phase >= 1:
        r_target = R_MOON + LUNAR_WORK_ALT
        if task_phase == 1:
            st, d_min = predicted_moon_extreme(high=False)
            point = T('飞掠近月点（刹车被捕获）')
            hint = T('这里相对月球跑得最快，反向点火减速最省燃料；减到推荐值就会被月球抓住。')
        else:
            _, _, _, _, peri_r, apo_r = moon_relative_elements()
            if abs(peri_r - r_target) > 0.2 * r_target:
                st, d_min = predicted_moon_extreme(high=True)
                point = T('环月远月点（减速压低近月点）')
                hint = T('在远月点减速，对面那个近月点就会被压低；先把它压到 500 km 高度。')
            else:
                st, d_min = predicted_moon_extreme(high=False)
                point = T('环月近月点（减速修圆）')
                hint = T('近月点速度最大，削到这里圆轨道需要的速度，远月点就被拉下来 —— 椭圆变圆。')
        if st is None or d_min is None:
            st, d_min = (x, y, vx, vy, moon_time), moon_relative_elements()[0]
        return st, point, moon_orbit_speed_for(d_min, r_target), hint
    if current_task == 5:
        r = max(float(np.hypot(x, y)), R_EARTH)
        if task_phase == 0:
            return (x, y, vx, vy, moon_time), T('当前位置（近地点，加速升轨）'), transfer_speed(r, HIGH_ORBIT_R), T('在近地点加速：这一端不动，对面的远地点被抬到 1200 km。')
        if task_phase == 1:
            st = predicted_apsis_state(True) or (x, y, vx, vy, moon_time)
            rr = max(float(np.hypot(st[0], st[1])), R_EARTH)
            return st, T('转移轨道远地点（补速修圆）'), circular_speed_at(rr), T('远地点跑得最慢，补到这里的圆轨道速度就能把椭圆撑圆。')
        if task_phase == 2:
            return (x, y, vx, vy, moon_time), T('当前位置（高轨，减速降轨）'), transfer_speed(r, LOW_ORBIT_R), T('在高轨道反向点火：这一端变远地点，对面的近地点被压到 300 km。')
        st = predicted_apsis_state(False) or (x, y, vx, vy, moon_time)
        rr = max(float(np.hypot(st[0], st[1])), R_EARTH)
        return st, T('转移轨道近地点（减速修圆）'), circular_speed_at(rr), T('近地点跑得最快，削到这里的圆轨道速度就能把椭圆修圆。')
    if current_task == 1 and task_phase == 1:
        cand = list(zip(*predicted)) if len(predicted[0]) else []
        cand = [(c[0], c[1], c[2], c[3], c[4]) for c in cand]
        if cand:
            radii = np.array([np.hypot(c[0], c[1]) for c in cand])
            best = int(np.argmax(radii))
            px, py, pvx, pvy, ts = cand[best]
        else:
            px, py, pvx, pvy, ts = x, y, vx, vy, moon_time
        r = max(np.hypot(px, py), R_EARTH)
        return (px, py, pvx, pvy, ts), T('转移轨道远地点'), circular_speed_at(r), T('远地点速度最慢，这里补一点速度就能把椭圆「抬」圆。')
    if current_task == 0:
        r = max(np.hypot(x, y), R_EARTH)
        return (x, y, vx, vy, moon_time), T('当前位置（近地点）'), circular_speed_at(r), T('现在跑得偏快，稍微减一点，椭圆就会变圆。')
    if current_task == 1:
        r = max(np.hypot(x, y), R_EARTH)
        a = (r + SYNC_ORBIT_RADIUS) / 2
        return (x, y, vx, vy, moon_time), T('近地点（向外加速）'), float(np.sqrt(MU_EARTH * (2 / r - 1 / a))), T('在近地点加速，远地点会被抬高；到了远地点还要再补一次。')
    if current_task == 2:
        r = max(np.hypot(x, y), R_EARTH)
        a = (r + MOON_ORBIT_RADIUS) / 2
        return (x, y, vx, vy, moon_time), T('近地点（朝月球方向出发）'), float(np.sqrt(MU_EARTH * (2 / r - 1 / a))), T('近地点加速后，椭圆的远端会一路延伸到月球轨道。')
    if current_task == 3:
        r = max(np.hypot(x, y), R_EARTH)
        return (x, y, vx, vy, moon_time), T('近地点（脱离地球）'), escape_speed_at(r) * 1.004, T('当地速度达到逃逸速度，轨迹就从椭圆变成不再闭合的双曲线。')
    r = max(np.hypot(x, y), R_EARTH)
    return (x, y, vx, vy, moon_time), T('近地点（继续加速）'), V3 + 0.2, T('第三宇宙速度约 16.7 km/s，到这里连太阳也拉不住它。')

TASK_TOLERANCE = (0.02, 0.015, 0.03, 0.0, 0.0, 0.015)

def lesson_of(index):
    '''指定任务在当前界面语言下的讲解数据。'''

    if UI_LANG == 'en':
        return TASK_LESSON_EN[index]
    return TASK_LESSON[index]

def current_lesson():
    '''当前任务"当前阶段"的讲解数据；多阶段任务会按阶段覆盖 core/body。'''

    base = lesson_of(current_task)
    phases = base.get('phase_lesson')
    if phases:
        if 0 <= task_phase < len(phases) and phases[task_phase]:
            merged = dict(base)
            merged.update(phases[task_phase])
            return merged
    return base

def current_target_range():
    '''
    返回当前任务当前阶段的合理速度范围 (lower, upper, best, note)。
    upper 为 None 表示没有上限（越快越好）。
    '''

    index = current_task
    try:
        _, _, best, _ = recommended_state()
    except Exception:
        best = circular_speed_at(max(np.hypot(x, y), R_EARTH))
    best = float(best)
    if index == 3:
        lower = escape_speed_at(max(np.hypot(x, y), R_EARTH))
        return lower, lower * 1.15, max(best, lower * 1.004), lesson_of(3)['range_note']
    if index == 4:
        return V3, None, max(best, V3 + 0.2), lesson_of(4)['range_note']
    tol = LUNAR_BURN_TOL if index == 2 and task_phase >= 1 else TASK_TOLERANCE[index]
    lower = best * (1 - tol)
    upper = best * (1 + tol)
    return lower, upper, best, current_lesson()['range_note']

def judge_preview_speed(speed):
    '''判断某个速度相对当前目标区间是偏慢 / 合适 / 偏快，返回 (状态码, 说明)。'''

    lower, upper, best, note = current_target_range()
    if upper is None:
        if speed >= lower:
            return 'ok', T('√ 已超过第三宇宙速度，连太阳也拉不住')
        return 'slow', T('还差 {a:.2f} km/s 才够 16.7').format(a=lower - speed)
    if speed < lower:
        return 'slow', T('偏慢 {a:.2f} km/s').format(a=lower - speed)
    if speed > upper:
        return 'fast', T('偏快 {a:.2f} km/s').format(a=speed - upper)
    return 'ok', T('√ 落在合理速度区间')

def sync_speed_widget(value=None):
    '''让仪表盘游标与滑块跟当前真实速度保持一致（不触发预览重算）。'''

    global _syncing_widget
    speed = current_speed() if value is None else float(value)
    speed = float(np.clip(speed, 0.0, SPEED_SLIDER_MAX))
    gauge_cursor.set_xdata([speed, speed])
    gauge_cursor_head.set_xdata([speed])
    if value is None:
        _syncing_widget = True
        try:
            speed_slider.set_val(speed)
            speed_input.set_val(f'{speed:.2f}')
        finally:
            _syncing_widget = False

def refresh_velocity_vector():
    vel = np.array([vx, vy], dtype=float)
    speed = float(np.linalg.norm(vel))
    if speed > 1e-9:
        direction = vel / speed
    else:
        r = max(np.hypot(x, y), R_EARTH)
        direction = np.array([-y, x]) / r
    vec_vel.set_positions((x, y), np.array([x, y]) + direction * 24000)
    vec_vel.set_visible(show_velocity)

def refresh_prediction(force=False):
    global last_predict_wall, predicted
    now = time.perf_counter()
    if not force:
        if now - last_predict_wall < PREDICT_REF_INTERVAL:
            return
    last_predict_wall = now
    predicted = predict_full_orbit(x, y, vx, vy, moon_time)
    line_predict.set_data(predicted[0], predicted[1])
    refresh_orbit_annotations()

def refresh_orbit_annotations():
    '''近/远地点标注，只在椭圆轨道且开关打开时显示。'''

    if not show_labels:
        peri_label.set_visible(False)
        apo_label.set_visible(False)
        return
    peri, apo, energy, ecc = peri_apo_now()
    if energy >= 0 or ecc < 0.001:
        peri_label.set_visible(False)
        apo_label.set_visible(False)
        return
    pos = np.array([x, y], dtype=float)
    vel = np.array([vx, vy], dtype=float)
    r = max(np.linalg.norm(pos), R_EARTH)
    ecc_vec = ((np.dot(vel, vel) - MU_EARTH / r) * pos - np.dot(pos, vel) * vel) / MU_EARTH
    direction = ecc_vec / max(np.linalg.norm(ecc_vec), 1e-9)
    p_pos = direction * peri
    a_pos = -direction * apo
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    def vis(p):
        if xlim[0] <= p[0] <= xlim[1]:
            return ylim[0] <= p[1] <= ylim[1]

    peri_label.set_position((p_pos[0], p_pos[1]))
    apo_label.set_position((a_pos[0], a_pos[1]))
    peri_label.set_visible(vis(p_pos))
    apo_label.set_visible(vis(a_pos))

def gravity_components(px, py, t):
    '''飞船（或任意点）处的引力加速度分量，返回 (地球拉力, 月球拉力)，km/s²。'''

    pos = np.array([px, py], dtype=float)
    re = max(float(np.linalg.norm(pos)), R_EARTH)
    acc_earth = -MU_EARTH * pos / re ** 3
    moon_pos, _ = moon_position(t)
    delta = np.asarray(moon_pos, dtype=float) - pos
    rm = max(float(np.linalg.norm(delta)), R_MOON)
    acc_moon = MU_MOON * delta / rm ** 3
    return acc_earth, acc_moon

def _fmt_accel(value_ms2):
    '''把 km/s² 转成学生熟悉的 m/s²，按量级自动选定点位数。'''

    v = float(value_ms2)
    if v >= 1.0:
        return f'{v:.2f}'
    if v >= 0.001:
        return f'{v:.4f}'
    return f'{v:.2e}'

def analyze_forces():
    '''
对飞船做完整的受力分析（纯计算，不碰画布）。

返回 dict，单位统一为 m/s²（学生熟悉的量级）：
  地球引力 / 月球引力 / 合力大小、合力矢量、
  切向分量（沿速度，改变速率）、法向分量（垂直速度，改变方向）、
  圆轨道所需的向心加速度 v²/r、二者之比与结论。
'''

    ae, am = gravity_components(x, y, moon_time)
    me, mm = float(np.linalg.norm(ae)), float(np.linalg.norm(am))
    total = ae + am
    mt = float(np.linalg.norm(total))
    vel = np.array([vx, vy], dtype=float)
    speed = float(np.linalg.norm(vel))
    vhat = vel / speed if speed > 1e-9 else np.array([1.0, 0.0])
    a_tan = float(np.dot(total, vhat))
    a_norm_vec = total - a_tan * vhat
    a_norm = float(np.linalg.norm(a_norm_vec))
    share_earth = me / max(me + mm, 1e-30)
    mp, moon_vel = moon_position(moon_time)
    if share_earth >= 0.5:
        center_name = '地球'
        r_ref = max(float(np.hypot(x, y)), R_EARTH)
        v_ref = speed
        radial_v = (x * vx + y * vy) / r_ref
    else:
        center_name = '月球'
        rel = np.array([x - mp[0], y - mp[1]], dtype=float)
        r_ref = max(float(np.linalg.norm(rel)), R_MOON)
        rel_v = vel - np.asarray(moon_vel, dtype=float)
        v_ref = float(np.linalg.norm(rel_v))
        radial_v = float(np.dot(rel, rel_v)) / r_ref
    need = v_ref ** 2 / r_ref if r_ref > 0 else 0.0
    ratio = a_norm / max(need, 1e-30)
    if ratio > 1.05:
        verdict = T('向心力过剩，轨道向{a}一侧弯').format(a=T(center_name))
    elif ratio < 0.95:
        verdict = T('引力拉不住，轨道被甩向外侧')
    else:
        verdict = T('引力刚好等于需要的向心力 —— 这就是圆轨道')
    return {'earth': me * 1000.0, 'moon': mm * 1000.0, 'total': mt * 1000.0, 'vec': total, 'tan': a_tan * 1000.0, 'norm': a_norm * 1000.0, 'need': need * 1000.0, 'ratio': ratio, 'center': center_name, 'share_earth': share_earth, 'radial_v': radial_v, 'verdict': verdict, 'speed': speed}

def _force_arrow(arrow, text, pos, direction, length, label, showable=True):
    '''画一支从飞船出发的受力箭头，并在箭头尖端外侧标名字。'''

    d = direction / max(float(np.linalg.norm(direction)), 1e-30)
    arrow.set_positions(tuple(pos), tuple(pos + d * length))
    arrow.set_visible(True)
    tip = pos + d * length * 1.16
    text.set_position((tip[0], tip[1]))
    text.set_text(label)
    text.set_visible(showable)

def refresh_force_analysis():
    '''
    受力分析的绘制入口：三支受力矢量 + 切向/法向分解 + 左侧数值面板。
    关闭时把所有相关 artist 隐藏；打开时才计算，避免白费开销。
    '''

    global last_force_report, last_gravity_sum
    arts = grav_arrow_earth, grav_arrow_moon, grav_arrow_sum, grav_arrow_tan, grav_arrow_norm, grav_text_earth, grav_text_moon, grav_text_tan, grav_text_norm
    if not show_force_analysis:
        for art in arts:
            art.set_visible(False)
        force_panel_bg.set_visible(False)
        for line in force_panel_lines:
            line.set_visible(False)
        return
    info = analyze_forces()
    last_force_report = info
    ae, am = gravity_components(x, y, moon_time)
    total = info['vec']
    last_gravity_sum = total
    _, _, span_x = current_view()
    w, h = canvas_px()
    base = 0.055 * min(span_x, span_x * (h / max(w, 1.0)))
    pos = np.array([x, y], dtype=float)
    me, mm = info['earth'] / 1000.0, info['moon'] / 1000.0
    s = max(me + mm, 1e-30)
    share_e, share_m = me / s, mm / s
    _force_arrow(grav_arrow_earth, grav_text_earth, pos, ae, base * min(0.35 + 1.6 * share_e, 1.6), T('地球引力'), share_e > 0.1)
    _force_arrow(grav_arrow_moon, grav_text_moon, pos, am, base * min(0.25 + 1.6 * share_m, 1.6), T('月球引力'), share_m > 0.1)
    dsum = total / max(float(np.linalg.norm(total)), 1e-30)
    grav_arrow_sum.set_positions(tuple(pos), tuple(pos + dsum * base * 1.1))
    grav_arrow_sum.set_visible(True)
    vel = np.array([vx, vy], dtype=float)
    speed = float(np.linalg.norm(vel))
    vhat = vel / speed if speed > 1e-9 else np.array([1.0, 0.0])
    nvec = np.array([-vhat[1], vhat[0]])
    tan_dir = vhat * (1.0 if info['tan'] >= 0 else -1.0)
    tan_len = base * max(0.35, 1.5 * abs(info['tan']) / 1000.0 / max(info['total'] / 1000.0, 1e-30))
    _force_arrow(grav_arrow_tan, grav_text_tan, pos, tan_dir, tan_len, T('切向'))
    norm_dir = total - float(np.dot(total, vhat)) * vhat
    if float(np.linalg.norm(norm_dir)) < 1e-30:
        norm_dir = nvec
    norm_len = base * max(0.35, 1.5 * info['norm'] / 1000.0 / max(info['total'] / 1000.0, 1e-30))
    _force_arrow(grav_arrow_norm, grav_text_norm, pos, norm_dir, norm_len, T('法向'))
    tan_state = T('速率在变大') if info['tan'] > 0 else T('速率在变小') if info['tan'] < 0 else T('速率不变')
    alt_state = T('正在升高') if info['radial_v'] > 0.02 else T('正在降低') if info['radial_v'] < -0.02 else T('基本不变')
    cmp_op = '>' if info['ratio'] > 1.05 else '<' if info['ratio'] < 0.95 else '≈'
    rows = [
        (T('受力分析 · 飞船（按 F 关闭）'), C_AMBER),
        (T('地球引力 {a} m/s²   指向地心').format(a=_fmt_accel(info['earth'])), C_BLUE),
        (T('月球引力 {a} m/s²   指向月心').format(a=_fmt_accel(info['moon'])), C_PURPLE),
        (T('合力 {a} m/s²   （地球占 {b:.1f}%）').format(a=_fmt_accel(info['total']), b=info['share_earth'] * 100), '#ffffff'),
        (T('切向分量 {a:+.3f} m/s²   {b}').format(a=info['tan'], b=tan_state), C_AMBER),
        (T('法向分量 {a} m/s²   负责让轨道拐弯').format(a=_fmt_accel(info['norm'])), C_CYAN),
        (T('绕{a}圆轨道需要 v²/r = {b} m/s²').format(a=T(info['center']), b=_fmt_accel(info['need'])), C_DIM),
        (T('引力 {a} {b} {c} → {d}').format(a=_fmt_accel(info['norm']), b=cmp_op, c=_fmt_accel(info['need']), d=info['verdict']),
         C_GREEN if 0.95 <= info['ratio'] <= 1.05 else C_AMBER),
        (T('高度：{a}（径向速度 {b:+.2f} km/s）').format(a=alt_state, b=info['radial_v']), C_TEXT),
    ]
    force_panel_bg.set_visible(True)
    for i, line in enumerate(force_panel_lines):
        if i < len(rows):
            text, color = rows[i]
            line.set_text(text)
            line.set_color(color)
            line.set_visible(True)
        else:
            line.set_visible(False)
    return info['total']

def toggle_force_analysis():
    '''按 F 键（或点标题栏按钮）开关受力分析。'''

    global show_force_analysis
    show_force_analysis = not show_force_analysis
    refresh_force_analysis()
    try:
        btn_force.label.set_color('#ffffff' if show_force_analysis else C_DIM)
        btn_force.color = '#1f4f73' if show_force_analysis else '#1a2734'
        btn_force.ax.set_facecolor(btn_force.color)
    except Exception:
        pass
    if show_force_analysis:
        toast(T('受力分析已打开：白=合力，蓝/紫=地球/月球引力，虚线=切向(改速率)与法向(改方向)'), 4.6, 'info')
    else:
        toast(T('受力分析已关闭（按 F 重新打开）'), 2.2, 'info')
    if not HEADLESS:
        fig.canvas.draw_idle()

def refresh_hud():
    name = classify_orbit(x, y, vx, vy, moon_time)
    tail = f'\n{msg}' if msg else ''
    mp, _ = moon_position(moon_time)
    moon_dist = float(np.linalg.norm(np.array([x - mp[0], y - mp[1]])))
    if moon_dist < MOON_SOI_RADIUS:
        _, v_rel, _, ecc_rel, peri_r, apo_r = moon_relative_elements()
        hud_text.set_text(T('相对月球 {a:.2f} km/s   距月面 {b:,.0f} km\n当前轨道：{c}（近月点 {d:,.0f} km，e = {e:.2f}）{f}').format(a=v_rel, b=moon_dist - R_MOON, c=name, d=peri_r - R_MOON, e=ecc_rel, f=tail))
    else:
        speed = float(np.hypot(vx, vy))
        altitude = float(np.hypot(x, y)) - R_EARTH
        hud_text.set_text(T('速度 {a:.2f} km/s   高度 {b:,.0f} km\n当前轨道：{c}{f}').format(a=speed, b=altitude, c=name, f=tail))
    refresh_target_band()

def refresh_card():
    phases = TASK_PHASE_NAMES[current_task]
    step = T(' · 第 {a}/{b} 步：{c}').format(a=task_phase + 1, b=len(phases), c=phase_name()) if len(phases) > 1 else ''
    card_no.set_text(T('任务 {a} / {b}{c}').format(a=current_task + 1, b=TASK_COUNT, c=step))
    card_name.set_text(f'{TASK_ICONS[current_task]} {T(TASK_NAMES[current_task])}')
    card_goal.set_text(T(TASK_GOALS[current_task]))
    if card_page == 0:
        items = task_checklist()
        for i, line in enumerate(check_lines):
            if i < len(items):
                title, ok, detail = items[i]
                line.set_text(f'{'√' if ok else '○'}  {title}   {detail}')
                line.set_color(C_GREEN if ok else C_DIM)
                line.set_visible(True)
            else:
                line.set_visible(False)
        try:
            state, point_name, target, hint = recommended_state()
        except Exception:
            state, point_name, target, hint = (x, y, vx, vy, moon_time), T('当前位置'), circular_speed_at(max(np.hypot(x, y), R_EARTH)), ''
        suffix = T('（相对月球）') if burn_frame() == 'moon' else ''
        guide_point.set_text(T('建议点火点：{a}').format(a=point_name))
        guide_speed.set_text(T('推荐速度 ≈ {a:.2f} km/s{b}').format(a=target, b=suffix))
        guide_hint.set_text(hint)
        card_peek.set_text(T('为什么：{a}  → 看「② 原理与案例」').format(a=lesson_of(current_task)['core']))
        guide_marker.set_data([state[0]], [state[1]])
        peri, apo, energy, ecc = peri_apo_now()
        speed = float(np.hypot(vx, vy))
        data_lines[0].set_text(T('速度 {a:.2f}   高度 {b:,.0f} km').format(a=speed, b=np.hypot(x, y) - R_EARTH))
        data_lines[1].set_text(T('近地点 {a:,.0f}   远地点 {b:,.0f} km').format(a=peri - R_EARTH, b=apo - R_EARTH) if np.isfinite(apo) else T('近地点 {a:,.0f} km   远地点 ∞').format(a=peri - R_EARTH))
        data_lines[2].set_text(T('偏心率 e = {a:.3f}   机械能 ε = {b:.2f}').format(a=ecc, b=energy))
    else:
        try:
            state = recommended_state()[0]
        except Exception:
            state = x, y, vx, vy, moon_time
    guide_marker.set_data([state[0]], [state[1]])
    if card_page == 1:
        refresh_lesson_page()

def refresh_lesson_page():
    '''填充讲解页：原理、合理速度范围（按当前位置实时计算）、现实案例。'''

    lesson = current_lesson()
    phases = TASK_PHASE_NAMES[current_task]
    step = T(' · 第 {a}/{b} 步：{c}').format(a=task_phase + 1, b=len(phases), c=phase_name()) if len(phases) > 1 else ''
    lesson_tag.set_text(T('任务 {a} / {b}{c} · {d}：为什么用这个速度？').format(a=current_task + 1, b=TASK_COUNT, c=step, d=T(TASK_NAMES[current_task])))
    lesson_core.set_text(lesson['core'])
    for i, line in enumerate(lesson_body):
        line.set_text(lesson['body'][i] if i < len(lesson['body']) else '')
    lower, upper, best, note = current_target_range()
    if upper is None:
        range_value.set_text(T('≥ {a:.2f} km/s（越快越好）').format(a=lower))
    else:
        range_value.set_text(f'{lower:.2f} ~ {upper:.2f} km/s')
    suffix = T('（相对月球）') if burn_frame() == 'moon' else ''
    range_note.set_text(T('推荐 {a:.2f} km/s{b}。{c}').format(a=best, b=suffix, c=note))
    status, detail = judge_preview_speed(current_speed())
    if not attempt_started:
        range_judge.set_text(T('现在还没点火，先用滑块预览虚线'))
        range_judge.set_color(C_DIM)
    else:
        range_judge.set_text(T('当前速度 {a}').format(a=detail))
        range_judge.set_color(C_GREEN if status == 'ok' else C_AMBER)
    for i, (name_line, detail_line) in enumerate(zip(case_names, case_details)):
        if i < len(lesson['cases']):
            name_line.set_text(f'· {lesson['cases'][i][0]}')
            detail_line.set_text(f'   {lesson['cases'][i][1]}')
        else:
            name_line.set_text('')
            detail_line.set_text('')
    trivia_head.set_text(T('拓展知识：{a}').format(a=lesson['trivia']))

def refresh_task_badges():
    mark_ui_dirty()
    for i, btn in enumerate(task_buttons):
        active = i == current_task
        done = task_done[i]
        if active:
            btn.color = '#1f4f73'
            btn.hovercolor = '#2b6d9c'
            btn.label.set_color('#ffffff')
            btn.label.set_weight('bold')
        elif done:
            btn.color = '#153227'
            btn.hovercolor = '#1f4a3a'
            btn.label.set_color(C_GREEN)
            btn.label.set_weight('normal')
        else:
            btn.color = '#1a2734'
            btn.hovercolor = '#2f3f4f'
            btn.label.set_color(C_DIM)
            btn.label.set_weight('normal')
        btn.ax.set_facecolor(btn.color)
        label = f'{'√ ' if done else TASK_ICONS[i]} {T(TASK_SHORT[i])}'
        btn.label.set_text(label)
        continue

def switch_card_page(page):
    '''在「任务与操作」和「原理与案例」两页之间切换。'''

    global card_page
    card_page = page
    for group_index, group in enumerate(_card_groups):
        visible = group_index == page
        for artist in group:
            artist.set_visible(visible)
    for index, button in enumerate(card_tab_buttons):
        active = index == page
        button.color = '#1f4f73' if active else '#1a2734'
        button.hovercolor = '#2b6d9c' if active else '#2f3f4f'
        button.ax.set_facecolor(button.color)
        button.label.set_color('#ffffff' if active else C_DIM)
        button.label.set_weight('bold' if active else 'normal')
    refresh_card()
    if page == 1:
        toast(T('已打开讲解：{a}').format(a=lesson_of(current_task)['core']), 3.6, 'success')
    fig.canvas.draw_idle()

def select_task(index):
    reset_task(index, keep_view=True)
    toast(T('已切换到任务 {a}：{b}，飞船回到起点轨道').format(a=index + 1, b=T(TASK_NAMES[index])), 3.0, 'info')

def toggle_pause(event=None):
    global paused, msg
    if collision_state:
        toast(T('飞船已经撞上{a}，请点「重新发射」再来一次').format(a=T(collision_state)), 3.0, 'warn')
        return
    paused = not paused
    btn_pause.label.set_text(T('继续') if paused else T('暂停'))
    msg = T('已暂停，趁现在看清轨道形状') if paused else ''
    refresh_hud()
    fig.canvas.draw_idle()

def on_rate_change(value):
    if _syncing_widget:
        return
    set_simulation_rate(float(value))

def set_simulation_rate(value):
    '''设置仿真倍速（0.25× ~ 16×），滑块与读数同步。'''

    global simulation_rate, _syncing_widget
    simulation_rate = round(float(np.clip(value, RATE_MIN, RATE_MAX)) / RATE_STEP) * RATE_STEP
    simulation_rate = float(np.clip(simulation_rate, RATE_MIN, RATE_MAX))
    _syncing_widget = True
    try:
        rate_slider.set_val(simulation_rate)
    finally:
        _syncing_widget = False
    rate_slider.valtext.set_text(f'{simulation_rate:g}×')
    fig.canvas.draw_idle()

def _set_preview(value):
    '''拖动滑块/改输入框时，用当前（或已选中的）位置预演该速度下的轨道。'''

    global preview_speed, preview_traj, preview_info
    if _syncing_widget:
        return
    preview_speed = float(np.clip(value, SLIDER_MIN_SPEED, MAX_INPUT_SPEED))
    speed_slider.valtext.set_text(f'{preview_speed:.2f} km/s')
    base = pending_state if pending_state is not None else (x, y, vx, vy, moon_time)
    px, py, pvx, pvy, ts = base
    lunar = burn_frame() == 'moon'
    if lunar:
        _, moon_vel = moon_position(ts)
        rel_v = np.array([pvx, pvy], dtype=float) - np.asarray(moon_vel, dtype=float)
        sp = float(np.linalg.norm(rel_v))
        direction = rel_v / sp if sp > 1e-9 else np.array([1.0, 0.0])
        nv = np.asarray(moon_vel, dtype=float) + direction * preview_speed
    else:
        vel = np.array([pvx, pvy], dtype=float)
        sp = float(np.linalg.norm(vel))
        if sp > 1e-9:
            direction = vel / sp
        else:
            r = max(np.hypot(px, py), R_EARTH)
            direction = np.array([-py, px]) / r
        nv = direction * preview_speed
    nvx, nvy = float(nv[0]), float(nv[1])
    traj = predict_full_orbit(px, py, nvx, nvy, ts, steps=2200)
    preview_traj = traj[0], traj[1]
    line_preview.set_data(traj[0], traj[1])
    kind = classify_orbit(px, py, nvx, nvy, ts)
    status, judge_detail = judge_preview_speed(preview_speed)
    if lunar:
        _, _, e_rel, ecc_rel, peri_r, apo_r = moon_relative_elements(px, py, nvx, nvy, ts)
        if e_rel < 0:
            preview_info = T('（相对月球）{a:.2f} km/s → {b}｜近月点 {c:,.0f} km｜远月点 {d:,.0f} km｜e = {e:.3f}｜{f}').format(a=preview_speed, b=kind, c=peri_r - R_MOON, d=apo_r - R_MOON, e=ecc_rel, f=judge_detail)
        else:
            r_now = moon_relative_elements(px, py, nvx, nvy, ts)[0]
            preview_info = T('×（相对月球）{a:.2f} km/s 仍超过逃逸速度 {b:.2f} km/s —— 抓不住，会飞掠而过｜{c}').format(a=preview_speed, b=moon_escape_speed(r_now), c=judge_detail)
        preview_text.set_text(preview_info)
        preview_text.set_color(C_GREEN if status == 'ok' else C_AMBER)
        gauge_preview_head.set_data([min(preview_speed, SPEED_SLIDER_MAX)], [0.0])
        btn_fire.label.set_text(T('点 火（按 Enter）'))
        fig.canvas.draw_idle()
        return
    peri, apo, energy, ecc = apoapsis_periapsis(px, py, nvx, nvy)
    apo_txt = '∞' if not np.isfinite(apo) else f'{apo - R_EARTH:,.0f} km'
    preview_info = T('若以 {a:.2f} km/s 点火 → {b}｜e = {c:.3f}｜远地点 {d}｜{e}').format(a=preview_speed, b=kind, c=ecc, d=apo_txt, e=judge_detail)
    preview_text.set_text(preview_info)
    preview_text.set_color(C_GREEN if status == 'ok' else C_AMBER)
    min_r = float(np.min(np.hypot(traj[0], traj[1]))) if len(traj[0]) else np.hypot(px, py)
    if len(traj[0]) < 5 or min_r < R_EARTH + 100:
        preview_text.set_text(T('× {a:.2f} km/s 太慢了！这条预览线会撞进地球，速度要升到虚线参考值附近才飞得起来').format(a=preview_speed))
        preview_text.set_color(C_RED)
    gauge_preview_head.set_data([min(preview_speed, SPEED_SLIDER_MAX)], [0.0])
    btn_fire.label.set_text(T('点 火（按 Enter）'))
    fig.canvas.draw_idle()

speed_slider.on_changed(_set_preview)
speed_input.on_submit((lambda text: _apply_text_speed(text)))

def _apply_text_speed(text):
    try:
        value = float((text or '').strip())
    except ValueError:
        toast(T('请输入数字，例如 7.90（单位 km/s）'), 3.0, 'warn')
    else:
        if not 0 < value <= MAX_INPUT_SPEED:
            toast(T('速度要大于 0、不超过 {a:g} km/s').format(a=MAX_INPUT_SPEED), 3.0, 'warn')
            return
        _set_preview(value)
        speed_slider.set_val(min(value, SPEED_SLIDER_MAX))

def clear_preview():
    global preview_speed, preview_info
    preview_speed = None
    preview_info = ''
    line_preview.set_data([], [])
    gauge_preview_head.set_data([], [])
    preview_text.set_text(T('拖动滑块：亮青色虚线就是「如果现在点火」的轨道'))
    preview_text.set_color(C_CYAN)
    fig.canvas.draw_idle()

def fill_recommended_speed():
    try:
        _, _, target, _ = recommended_state()
    except Exception:
        target = circular_speed_at(max(np.hypot(x, y), R_EARTH))
    _set_preview(target)
    speed_slider.set_val(min(target, SPEED_SLIDER_MAX))
    speed_input.set_val(f'{target:.2f}')
    toast(T('已填入推荐速度 {a:.2f} km/s，看虚线满意了再点火').format(a=target), 3.0, 'info')

def stash_comparison():
    global comparison_traj
    old_x = np.asarray(trail_x, dtype=float)
    old_y = np.asarray(trail_y, dtype=float)
    if len(predicted[0]):
        old_x = np.append(old_x, predicted[0]) if len(old_x) else predicted[0]
        old_y = np.append(old_y, predicted[1]) if len(old_y) else predicted[1]
    comparison_traj = old_x.copy(), old_y.copy()
    line_compare.set_data(comparison_traj[0], comparison_traj[1])
    line_compare.set_visible(show_compare and len(comparison_traj[0]) > 0)

def apply_burn(speed):
    '''在当前（或已选中的）位置施加一次瞬时切向脉冲。'''

    global pending_state, vx, vy, mission_started, attempt_started, collision_state, msg
    if collision_state:
        toast(T('飞船已经撞上{a}，请先点「重新发射」').format(a=T(collision_state)), 3.0, 'error')
        return
    stash_comparison()
    if pending_state is not None:
        set_state(*pending_state)
        pending_state = None
        selected_marker.set_data([], [])
    if burn_frame() == 'moon':
        moon_pos, moon_vel = moon_position(moon_time)
        rel_v = np.array([vx, vy], dtype=float) - np.asarray(moon_vel, dtype=float)
        sp = float(np.linalg.norm(rel_v))
        if sp > 1e-9:
            direction = rel_v / sp
        else:
            rel_p = np.array([x - moon_pos[0], y - moon_pos[1]], dtype=float)
            rn = max(float(np.linalg.norm(rel_p)), R_MOON)
            direction = np.array([-rel_p[1], rel_p[0]]) / rn
        new_v = np.asarray(moon_vel, dtype=float) + direction * float(speed)
    else:
        vel = np.array([vx, vy], dtype=float)
        sp = float(np.linalg.norm(vel))
        if sp > 1e-9:
            direction = vel / sp
        else:
            r = max(np.hypot(x, y), R_EARTH)
            direction = np.array([-y, x]) / r
        new_v = direction * float(speed)
    vx, vy = float(new_v[0]), float(new_v[1])
    trail_x.clear()
    trail_y.clear()
    history_states.clear()
    trail_x.append(x)
    trail_y.append(y)
    history_states.append((x, y, vx, vy, moon_time))
    line_orbit.set_data(list(trail_x), list(trail_y))
    mission_started = True
    attempt_started = True
    collision_state = ''
    clear_preview()
    refresh_velocity_vector()
    sync_speed_widget()
    refresh_prediction(force=True)
    refresh_orbit_annotations()
    if burn_frame() == 'moon':
        _, _, e_rel, ecc_rel, peri_r, _ = moon_relative_elements()
        if e_rel < 0:
            msg = T('已被月球捕获：环月轨道近月点 {a:,.0f} km，e = {b:.2f}').format(a=peri_r - R_MOON, b=ecc_rel)
        else:
            msg = T('还没被月球捕获：相对月球速度仍超过逃逸速度，会飞掠而过，要继续减速')
    elif speed >= V3:
        msg = T('已达第三宇宙速度，太阳也拉不住它了')
    elif speed >= V2:
        msg = T('已达第二宇宙速度，可以飞离地球')
    elif speed >= V1:
        msg = T('速度变大，轨道远端被抬高')
    else:
        msg = T('速度变小，轨道会往地球这边塌')
    refresh_hud()
    check_completion()
    fig.canvas.draw_idle()

def fire(event=None):
    '''点火：优先用滑块预览值。'''

    if preview_speed is not None:
        apply_burn(preview_speed)
        return
    apply_burn(float(np.clip(speed_slider.val, SLIDER_MIN_SPEED, MAX_INPUT_SPEED)))

def jump_to_recommended(event=None):
    '''把飞船挪到推荐点火点（通常是近地点或转移轨道远地点）。'''

    global pending_state
    try:
        state, point_name, target, hint = recommended_state()
    except Exception:
        toast(T('暂时找不到推荐点，先让飞船飞一会儿再试'), 3.0, 'warn')
    else:
        set_state(*state)
        pending_state = None
        selected_marker.set_data([], [])
        trail_x.clear()
        trail_y.clear()
        trail_x.append(x)
        trail_y.append(y)
        line_orbit.set_data(list(trail_x), list(trail_y))
        rocket_point.set_data([x], [y])
        rocket_halo.set_center((x, y))
        update_moon_texture(moon_position(moon_time)[0])
        refresh_velocity_vector()
        refresh_prediction(force=True)
        sync_speed_widget()
        toast(T('已跳到{a}，推荐速度约 {b:.2f} km/s').format(a=point_name, b=target), 3.2, 'info')
        refresh_card()
        refresh_hud()
        fig.canvas.draw_idle()

def toggle_point_selection(event=None):
    global selecting_point, pending_state
    selecting_point = not selecting_point
    if selecting_point:
        pending_state = None
        selected_marker.set_data([], [])
        btn_select_point.label.set_text(T('取消选点'))
        toast(T('请在左侧轨迹线上点击，选下一次点火的位置'), 3.5, 'info')
    else:
        btn_select_point.label.set_text(T('在轨迹上选点'))
    fig.canvas.draw_idle()

def rebuild_ui_rects():
    '''收集所有控件的占位矩形：落在这些地方的鼠标事件交给控件，不用于拖拽/缩放。'''

    _ui_rects.clear()
    if immersive:
        p = ax_immersive.get_position()
        _ui_rects.append((p.x0, p.y0, p.x1, p.y1))
        return
    for a in fig.axes:
        if a is star_ax or a is ax or a is panel_ax or not a.get_visible():
            continue
        p = a.get_position()
        _ui_rects.append((p.x0, p.y0, p.x1, p.y1))
    _ui_rects.extend(_group_rects)

def point_over_ui(event):
    '''鼠标是否压在某个按钮/滑块/分组框上。'''

    if event.x is None or event.y is None:
        return True
    w, h = canvas_px()
    if w < 2 or h < 2:
        return True
    fx, fy = event.x / w, event.y / h
    pad = 0.004
    for x0, y0, x1, y1 in _ui_rects:
        if x0 - pad <= fx <= x1 + pad:
            if y0 - pad <= fy <= y1 + pad:
                return True
    return False

def set_follow_view(flag):
    '''手动平移视角时会关掉"视角跟随"，并让复选框状态保持一致。'''

    global follow_view
    follow_view = bool(flag)
    try:
        index = 3
        if check.get_status()[index] != follow_view:
            check.set_active(index)
            return
    except Exception:
        pass

drag_state = {'active': False, 'x': 0.0, 'y': 0.0}
dragging = False
_drag_hinted = False

def on_mouse_press(event):
    '''左键按下：优先让"选点模式"取点，否则开始拖拽平移视图。'''

    global dragging, _drag_hinted
    if event.button != 1 or event.x is None or point_over_ui(event):
        return None
    was_selecting = selecting_point
    on_plot_click(event)
    if was_selecting:
        return
    dragging = True
    drag_state['x'] = event.x
    drag_state['y'] = event.y
    if follow_view:
        set_follow_view(False)
    if not _drag_hinted:
        _drag_hinted = True
        toast(T('已经在平移视角了：拖动改变位置，滚轮缩放，「复位视角」回到全景'), 3.0)

def on_mouse_move(event):
    if not dragging or event.x is None:
        return None
    prev = event_data_xy_at(drag_state['x'], drag_state['y'])
    now = event_data_xy_at(event.x, event.y)
    drag_state['x'], drag_state['y'] = event.x, event.y
    pan_view(prev[0] - now[0], prev[1] - now[1])
    refresh_orbit_annotations()
    refresh_locators()
    refresh_force_analysis()
    fig.canvas.draw_idle()

def on_mouse_release(event):
    global dragging
    if dragging:
        if event.button == 1:
            dragging = False

def event_data_xy(event):
    '''把鼠标像素位置换算成宇宙坐标（不依赖 event.inaxes，做法更稳）。'''

    inv = ax.transData.inverted()
    return inv.transform((event.x, event.y))

def event_data_xy_at(px, py):
    '''像素坐标 → 宇宙坐标。'''

    return ax.transData.inverted().transform((px, py))

def on_plot_click(event):
    global pending_state, selecting_point
    if not selecting_point or event.x is None or point_over_ui(event):
        return None
    candidates = list(history_states)
    if len(predicted[0]):
        candidates.extend(zip(predicted[0], predicted[1], predicted[2], predicted[3], predicted[4]))
    if not candidates:
        toast(T('还没有可点的轨迹，先点火让飞船飞一段'), 3.0, 'warn')
        return
    pts = np.asarray([[c[0], c[1]] for c in candidates])
    screen = ax.transData.transform(pts)
    dist = np.hypot(screen[:, 0] - event.x, screen[:, 1] - event.y)
    nearest = int(np.argmin(dist))
    if dist[nearest] > 20:
        toast(T('要点在轨迹线上哦，再靠近一点'), 2.6, 'warn')
        return
    pending_state = tuple((float(v) for v in candidates[nearest]))
    selected_marker.set_data([pending_state[0]], [pending_state[1]])
    selecting_point = False
    btn_select_point.label.set_text('在轨迹上选点')
    toast(T('点火位置已选定，下一步调速度再点火'), 3.0, 'info')
    fig.canvas.draw_idle()

def on_observation_toggle(label):
    global show_labels, show_velocity, show_compare, follow_view
    idx = -1
    for i, key in enumerate(OBS_TOGGLES):
        if not label in (key, T(key)):
            continue
        idx = i
        break
    if idx == 0:
        show_labels = not show_labels
        refresh_orbit_annotations()
    elif idx == 1:
        show_velocity = not show_velocity
        vec_vel.set_visible(show_velocity)
    elif idx == 2:
        show_compare = not show_compare
        line_compare.set_visible(show_compare and len(comparison_traj[0]) > 0)
    elif idx == 3:
        try:
            follow_view = bool(check.get_status()[3])
        except Exception:
            follow_view = not follow_view
        if follow_view:
            toast(T('视角跟随已打开：飞船靠近边缘时画面会自动跟过去'), 2.6)
    fig.canvas.draw_idle()

def capture_snapshot(event=None):
    '''最多保留 3 张轨道快照，方便 A/B 对比。'''

    flown_x = np.asarray(trail_x, dtype=float)
    flown_y = np.asarray(trail_y, dtype=float)
    snapshots.append({'orbit': classify_orbit(x, y, vx, vy, moon_time), 'speed': float(np.hypot(vx, vy)), 'flown_x': flown_x.copy(), 'flown_y': flown_y.copy(), 'future_x': np.asarray(predicted[0], dtype=float).copy(), 'future_y': np.asarray(predicted[1], dtype=float).copy()})
    del snapshots[:-3]
    for i, pax in enumerate(snapshot_axes):
        pax.clear()
        pax.set_facecolor('#0a1622')
        pax.set_xticks([])
        pax.set_yticks([])
        for sp in pax.spines.values():
            sp.set_color(C_EDGE)
            sp.set_linewidth(0.6)
        if i >= len(snapshots):
            pax.text(0.5, 0.5, T('空'), ha='center', va='center', fontsize=7, color='#3d5266', transform=pax.transAxes)
            continue
        s = snapshots[i]
        pax.plot(s['future_x'], s['future_y'], color='#8f9aa8', lw=0.5, linestyle='--')
        pax.plot(s['flown_x'], s['flown_y'], color=C_TRAIL, lw=0.7)
        all_x = np.concatenate([s['flown_x'], s['future_x'], [0.0]])
        all_y = np.concatenate([s['flown_y'], s['future_y'], [0.0]])
        xspan = max(float(np.ptp(all_x)), 15000.0)
        yspan = max(float(np.ptp(all_y)), 15000.0)
        pax.set_xlim(all_x.min() - 0.1 * xspan, all_x.max() + 0.1 * xspan)
        pax.set_ylim(all_y.min() - 0.1 * yspan, all_y.max() + 0.1 * yspan)
        pax.set_aspect('equal', adjustable='box')
        pax.set_title(f'{T(s['orbit'])} {s['speed']:.1f}km/s', fontsize=5.5, color=C_TEXT, pad=1)
        continue
    toast(T('已保存快照，最多留 3 张用于对比'), 2.4, 'info')
    fig.canvas.draw_idle()

def run_auto_demo(event=None):
    '''老师讲课时用：直接跳到标准解并执行。'''

    global auto_task
    state, point_name, target, hint = recommended_state()
    set_state(*state)
    apply_burn(target)
    auto_task = current_task
    if current_task == 1:
        toast(T('自动演示：第 1 步已把远地点抬到同步轨道，到第 2 步会自动修圆'), 4.0, 'info')
    else:
        toast(T('自动演示：已在{a}以 {b:.2f} km/s 点火').format(a=point_name, b=target), 3.5, 'info')
    if not HEADLESS:
        fig.canvas.draw_idle()

def fast_forward_to(state):
    '''
    自动演示专用：把飞船挪到指定状态。

    为了不让学生"看丢"转移段，会把预测轨迹上已经飞过的那一段补画成轨迹线，
    于是画面上仍然看得到完整的转移弧。
    '''

    idx = 0
    if len(predicted[4]):
        idx = int(np.argmin(np.abs(np.asarray(predicted[4], dtype=float) - float(state[4]))))
    set_state(*state)
    trail_x.clear()
    trail_y.clear()
    if idx > 2:
        step = max(1, idx // 400)
        trail_x.extend(np.asarray(predicted[0][:idx], dtype=float)[::step].tolist())
        trail_y.extend(np.asarray(predicted[1][:idx], dtype=float)[::step].tolist())
    trail_x.append(x)
    trail_y.append(y)
    history_states.clear()
    history_states.append((x, y, vx, vy, moon_time))
    line_orbit.set_data(list(trail_x), list(trail_y))
    rocket_point.set_data([x], [y])
    rocket_halo.set_center((x, y))
    update_moon_texture(moon_position(moon_time)[0])
    refresh_velocity_vector()
    refresh_prediction(force=True)
    sync_speed_widget()

def check_auto_step():
    '''自动演示：等飞船飞到该点火的位置，再自动施加下一步脉冲。'''

    global auto_task
    if auto_task is None or collision_state:
        return None
    r = float(np.hypot(x, y))
    radial = (x * vx + y * vy) / max(r, R_EARTH)
    if auto_task == 1:
        if r >= 0.96 * SYNC_ORBIT_RADIUS and radial <= 0:
            auto_task = None
            apply_burn(circular_speed_at(max(r, R_EARTH)))
            toast(T('自动演示：已在远地点补速，同步圆轨道完成！注意它的周期 ≈ 24 小时'), 4.5, 'success')
        return
    if auto_task == 2:
        if task_phase == 0:
            st, d_min = predicted_moon_extreme(high=False)
            if st is None or d_min is None or d_min > LUNAR_SOI_ENTER:
                return None
            fast_forward_to(st)
            apply_burn(moon_orbit_speed_for(d_min, R_MOON + LUNAR_WORK_ALT))
            toast(T('自动演示快进：真实转移要飞约 5 天，这里直接跳到近月点 {a:,.0f} km 高度刹车').format(a=d_min - R_MOON), 5.0, 'info')
            return
        if task_phase >= 1:
            r_rel, _, _, _, peri_r, _ = moon_relative_elements()
            if r_rel <= 1.06 * peri_r and moon_radial_velocity() >= 0:
                apply_burn(moon_circular_speed(r_rel))
                auto_task = None
                toast(T('自动演示：已在环月近月点减速，修成环月圆轨道'), 4.5, 'success')
        return
    if auto_task == 5:
        if task_phase == 1:
            if r >= 0.99 * HIGH_ORBIT_R and radial <= 0:
                apply_burn(circular_speed_at(r))
                toast(T('自动演示第 2 步：在远地点补速，把椭圆修成 1200 km 圆轨道'), 4.5, 'info')
            return
        if task_phase == 2:
            apply_burn(transfer_speed(r, LOW_ORBIT_R))
            toast(T('自动演示第 3 步：在高轨道减速，把近地点压到 300 km'), 4.5, 'info')
            return
        if task_phase == 3 and r <= 1.01 * LOW_ORBIT_R and radial >= 0:
            apply_burn(circular_speed_at(r))
            auto_task = None
            toast(T('自动演示第 4 步：在近地点减速，修成 300 km 圆轨道'), 4.5, 'success')

def check_completion():
    '''阶段推进 + 通关判定。多阶段任务靠 task_phase 一步步放行。'''

    global task_phase
    if not attempt_started:
        return
    if current_task == 1 and task_phase == 0:
        peri, apo, energy, ecc = peri_apo_now()
        if energy < 0 and peri > R_EARTH and ecc > 0.3 and 0.9 * SYNC_ORBIT_RADIUS <= apo <= 1.1 * SYNC_ORBIT_RADIUS:
            task_phase = 1
            toast(T('第 1 步达成！远地点已到同步轨道，接下来在远地点补速把椭圆修圆'), 4.5, 'success')
    elif current_task == 2 and task_phase == 0:
        mp, _ = moon_position(moon_time)
        dist = float(np.linalg.norm(np.array([x - mp[0], y - mp[1]])))
        if dist <= LUNAR_SOI_ENTER:
            task_phase = 1
            sync_speed_widget()
            toast(T('已进入月球引力范围！现在必须刹车减速，否则只是擦肩而过（速度滑块已改为相对月球）'), 5.2, 'success')
    elif current_task == 2 and task_phase == 1:
        r_rel, _, e_rel, _, _, _ = moon_relative_elements()
        if e_rel < 0 and r_rel < MOON_SOI_RADIUS:
            task_phase = 2
            toast(T('捕获成功！现在是绕月大椭圆，还要在拱点再减速才能修成环月圆轨道'), 5.0, 'success')
    elif current_task == 5 and task_phase == 0:
        peri, apo, energy, ecc = peri_apo_now()
        if energy < 0 and np.isfinite(apo) and ecc > 0.004 and abs(apo - HIGH_ORBIT_R) <= 0.03 * HIGH_ORBIT_R:
            task_phase = 1
            toast(T('第 1 步达成：远地点抬到 1200 km。现在飞到远地点补速，把椭圆修圆'), 5.0, 'success')
    elif current_task == 5 and task_phase == 1:
        peri, apo, energy, ecc = peri_apo_now()
        if ecc < 0.05 and abs((peri + apo) / 2 - HIGH_ORBIT_R) <= 0.03 * HIGH_ORBIT_R:
            task_phase = 2
            toast(T('第 2 步达成：1200 km 圆轨道。接下来在高轨道减速降轨'), 5.0, 'success')
    elif current_task == 5 and task_phase == 2:
        peri, apo, energy, ecc = peri_apo_now()
        mid = (HIGH_ORBIT_R + LOW_ORBIT_R) / 2
        if energy < 0 and abs(peri - LOW_ORBIT_R) <= 0.05 * LOW_ORBIT_R and abs((peri + apo) / 2 - mid) <= 0.05 * mid:
            task_phase = 3
            toast(T('第 3 步达成：近地点降到 300 km。最后飞到近地点再减速修圆'), 5.0, 'success')
    if task_is_complete():
        if not task_done[current_task]:
            task_done[current_task] = True
            refresh_task_badges()
            toast(T('闯关成功！你完成了「{a}」').format(a=T(TASK_NAMES[current_task])), 4.0, 'success')
            if all(task_done):
                toast(T('五个任务全部完成，你已经掌握速度如何决定轨道形状'), 5.0, 'success')

def resolve_collision():
    global collision_state, mission_started, paused
    hit = ''
    if np.hypot(x, y) <= R_EARTH:
        hit = '地球'
    else:
        mp, _ = moon_position(moon_time)
        if np.hypot(x - mp[0], y - mp[1]) <= R_MOON:
            hit = '月球'
    if hit:
        collision_state = hit
        mission_started = False
        paused = True
        btn_pause.label.set_text(T('已暂停'))
        toast(T('飞船撞上了{a}。速度太小，引力把它拉了回来，试试「重新发射」').format(a=T(hit)), 5.0, 'error')
        return True
    return False

def trail_gap():
    '''轨迹记录阈值随视野自适应：放得越大记得越密，近景轨迹才平滑。'''

    _, _, span_x = current_view()
    return float(np.clip(span_x * 0.0006, 40.0, 3000.0))

def advance():
    global moon_time, x, y, sim_time, vx, vy
    frame_seconds = COAST_FRAME_SECONDS * simulation_rate
    if not mission_started:
        moon_time += frame_seconds
        update_moon_texture(moon_position(moon_time)[0])
        return
    steps = max(1, int(np.ceil(frame_seconds / MAX_INTEGRATION_STEP)))
    dt = frame_seconds / steps
    for _ in range(steps):
        prev_gx, prev_gy = x, y
        a0 = gravity_acceleration(x, y, moon_time)
        v_half = np.array([vx, vy]) + a0 * (dt / 2)
        nx, ny = x + v_half[0] * dt, y + v_half[1] * dt
        nt = sim_time + dt
        x, y = nx, ny
        sim_time = nt
        moon_time += dt
        a1 = gravity_acceleration(x, y, moon_time)
        vel = v_half + a1 * (dt / 2)
        vx, vy = vel
        if resolve_collision():
            return
        if not trail_x or np.hypot(x - trail_x[-1], y - trail_y[-1]) > trail_gap():
            trail_x.append(x)
            trail_y.append(y)
        if len(history_states) == 0 or moon_time - history_states[-1][4] > 60.0:
            history_states.append((x, y, vx, vy, moon_time))
        _ = prev_gx, prev_gy
        continue

_dynamic_artists = []
_region_axes = {1: [], 2: []}
_bg_cache = None
_bg_size = (0, 0)
_ui_dirty = True
_frame_count = 0

def mark_ui_dirty():
    '''UI 有变化时调用：下一帧整窗重画并刷新缓存（否则改动不会显示）。'''

    global _ui_dirty
    _ui_dirty = True

def build_dynamic_artists():
    '''收集每帧都可能变化的 artist，按 zorder 排好绘制顺序。'''

    global _dynamic_artists
    scene = ('line_compare', 'line_predict', 'line_preview', 'line_orbit', 'line_recent', 'rocket_halo', 'rocket_point', 'selected_marker', 'guide_marker', 'vec_vel', 'grav_arrow_earth', 'grav_arrow_moon', 'grav_arrow_sum', 'grav_arrow_tan', 'grav_arrow_norm', 'grav_text_earth', 'grav_text_moon', 'grav_text_tan', 'grav_text_norm', 'earth_artist', 'moon_artist', 'earth_locator', 'moon_marker', 'moon_label', 'earth_label', 'peri_label', 'apo_label', 'hud_text', 'toast_patch', 'toast_text', 'force_panel_bg')
    out = []
    for nm in scene:
        art = globals().get(nm)
        if art is not None:
            out.append((ax, art))
    out.extend(((ax, t) for t in force_panel_lines))
    out.sort(key=(lambda pair: float(pair[1].get_zorder())))
    _dynamic_artists = out
    for idx in (1, 2):
        rx0, ry0, rx1, ry1 = BLIT_RECTS[idx]
        found = []
        for cand in fig.axes:
            if cand is star_ax or cand is ax:
                continue
            p = cand.get_position()
            if p.x0 >= rx0 and p.x1 <= rx1 and p.y0 >= ry0 and p.y1 <= ry1:
                found.append(cand)
        found.sort(key=(lambda z: float(z.get_zorder())))
        _region_axes[idx] = found

def _blit_boxes():
    '''
    把刷新区域换算成当前画布的像素矩形（取整，C 层要求整数）。

    沉浸模式下只有一块：整屏。不能沿用"太空主区 + 仪表盘 + 引导卡"三块，因为面板
    收起后那两块区域变成开阔宇宙，而 _draw_dynamic() 是先贴背景再画动态元素——
    后两块会把刚画在宇宙里的飞船擦掉，飞船飞到右边就凭空消失。
    '''

    rects = ((0.0, 0.0, 1.0, 1.0),) if immersive else BLIT_RECTS
    w, h = render_px()
    boxes = []
    for x0, y0, x1, y1 in rects:
        boxes.append(Bbox.from_bounds(int(round(x0 * w)), int(round(y0 * h)), int(round((x1 - x0) * w)), int(round((y1 - y0) * h))))
    return boxes

def _rebuild_cache(boxes):
    '''
    重建背景缓存：先把动态元素全部藏起来整窗画一次，得到"干净的星空 + UI"，
    再把三块区域的像素存下来。之后每帧只要恢复像素 + 重画动态元素即可。
    '''

    global _bg_cache, _bg_size, _ui_dirty
    canvas = fig.canvas
    states = [art.get_visible() for _, art in _dynamic_artists]
    for _, art in _dynamic_artists:
        art.set_visible(False)
    try:
        canvas.draw()
        _bg_cache = [canvas.copy_from_bbox(b) for b in boxes]
        _bg_size = render_px()
    finally:
        for (_, art), vis in zip(_dynamic_artists, states):
            art.set_visible(vis)
    _ui_dirty = False

def _draw_dynamic(boxes):
    '''blit 路径：恢复背景 → 重画动态元素 → 只把三块区域贴回屏幕。'''

    canvas = fig.canvas
    renderer = canvas.get_renderer()
    canvas.restore_region(_bg_cache[0])
    for owner, art in _dynamic_artists:
        if art.get_visible():
            owner.draw_artist(art)
    canvas.blit(boxes[0])
    if len(boxes) < 2:
        return
    canvas.restore_region(_bg_cache[1])
    for sub in _region_axes[1]:
        sub.draw(renderer)
    canvas.blit(boxes[1])
    if _frame_count % CARD_REDRAW_EVERY == 0:
        canvas.restore_region(_bg_cache[2])
        for sub in _region_axes[2]:
            sub.draw(renderer)
        canvas.blit(boxes[2])

def render_frame(force=False):
    '''画一帧：绝大多数帧只走 blit 路径，UI 变化时才整窗重画一次。'''

    if HEADLESS:
        return
    cw, ch = canvas_px()
    rw, rh = render_px()
    if abs(cw - rw) > 2 or abs(ch - rh) > 2:
        sync_canvas_size()
    boxes = _blit_boxes()
    stale = _bg_cache is None or len(_bg_cache) != len(boxes) or _bg_size != render_px()
    if force or stale or _ui_dirty or _frame_count % FULL_REDRAW_EVERY == 0:
        _rebuild_cache(boxes)
        _draw_dynamic(boxes)
        return
    try:
        _draw_dynamic(boxes)
    except Exception:
        _rebuild_cache(boxes)
        _draw_dynamic(boxes)

def _tick():
    '''定时器回调：推进一帧仿真并渲染。'''

    global _frame_count
    update(_frame_count)
    _frame_count += 1
    render_frame()

def start_animation():
    '''用画布定时器驱动动画（不用 FuncAnimation，因为它无法配合分层 blit）。'''

    timer = fig.canvas.new_timer(interval=ANIMATION_INTERVAL_MS)
    timer.add_callback(_tick)
    timer.start()
    return timer

def update(frame):
    global last_loop_wall
    now = time.perf_counter()
    gap = now - last_loop_wall
    last_loop_wall = now
    stalled = not HEADLESS and gap > STALL_GUARD_SECONDS
    if not paused and not stalled:
        advance()
        update_moon_texture(moon_position(moon_time)[0])
        check_auto_step()
        line_orbit.set_data(list(trail_x), list(trail_y))
        line_recent.set_data(list(trail_x)[-45:], list(trail_y)[-45:])
        rocket_point.set_data([x], [y])
        rocket_halo.set_center((x, y))
        refresh_velocity_vector()
        refresh_force_analysis()
        refresh_locators()
        follow_target_if_needed()
        refresh_prediction()
        refresh_orbit_annotations()
        check_completion()
        refresh_hud()
        refresh_card()
    update_toast()
    return line_orbit, line_recent, line_predict, line_preview, line_compare, rocket_point, vec_vel, selected_marker, guide_marker, hud_text, toast_text, rocket_halo

def show_tip(text, duration=3.0):
    '''给外部脚本用的便捷提示：3 秒后自动消失，不打断课堂。'''

    toast(text, duration, 'info')

def on_scroll(event):
    '''滚轮缩放：以光标为焦点，等比缩放，并把视野宽度限制在不丢飞船的范围内。'''

    if event.x is None or event.y is None or point_over_ui(event):
        return None
    if event.button in ('up', 4):
        factor = 0.8333333333333334
    elif event.button in ('down', 5):
        factor = 1.2
    else:
        return
    fx, fy = event_data_xy(event)
    zoom_view(factor, fx, fy)
    refresh_orbit_annotations()
    refresh_locators()
    refresh_force_analysis()
    fig.canvas.draw_idle()

def on_resize(event):
    '''窗口大小变化后重新配平竖直跨度，保证 1 km 横竖一样长。'''

    sync_canvas_size()
    mark_ui_dirty()
    sync_view_aspect()
    refresh_orbit_annotations()
    refresh_force_analysis()
    fig.canvas.draw_idle()

fullscreen = False

def toggle_fullscreen(event=None):
    '''F11 全屏：投影时去掉标题栏，画面铺满整块屏幕。'''

    global fullscreen
    if HEADLESS:
        return
    fullscreen = not fullscreen
    try:
        fig.canvas.manager.window.attributes('-fullscreen', fullscreen)
    except Exception:
        fullscreen = False

def maximize_for_projector():
    '''
    启动后把窗口铺到最大，但别让画布超出像素预算。

    Tk 后端会按屏幕的物理像素给 figure 定 dpi，最大化之后 2560×1600 的屏能得到
    380 万像素的画布。而每帧开销几乎全随像素数线性增长：blit 一次 32 ms、重画
    全部动态元素 37 ms，一帧接近 70 ms，投影时明显拖影。压到 260 万像素一帧能省
    掉一大半；1080p 的投影仪本来就不到这个数，所以正常教室根本不会触发缩放，
    只有高分屏笔记本才会——而这时画面依然铺满了大半个屏幕，不会出现黑边。
    '''

    win = fig.canvas.manager.window
    try:
        win.wm_state('zoomed')
        for _ in range(6):
            win.update()
            win.update_idletasks()
        sw, sh = win.winfo_width(), win.winfo_height()
        if sw < 200 or sh < 200 or sw * sh <= MAX_RENDER_PIXELS:
            return None
        k = (MAX_RENDER_PIXELS / float(sw * sh)) ** 0.5
        win.wm_state('normal')
        win.geometry('%dx%d+%d+%d' % (int(sw * k), int(sh * k),
                                      max(0, (sw - int(sw * k)) // 2),
                                      max(0, (sh - int(sh * k)) // 2)))
    except Exception:
        return

def set_ui_language(lang):
    '''
切换界面语言（"zh" 中文 / "en" English）。

三层文本分别处理：
  1) _LANG_ARTISTS 里登记的静态文本（标题、按钮、图例）逐个重设；
  2) 依当前状态重设动态按钮文案（暂停/选点/沉浸等）；
  3) 调一遍各刷新函数，让 HUD、引导卡、受力面板、提示条全部按新语言重算。
'''

    global UI_LANG
    if lang not in ('zh', 'en') or lang == UI_LANG:
        return None
    UI_LANG = lang
    for artist, zh in _LANG_ARTISTS:
        try:
            artist.set_text(T(zh))
        except Exception:
            continue
    btn_pause.label.set_text(T('已暂停') if collision_state else T('继续') if paused else T('暂停'))
    btn_fire.label.set_text(T('点 火（按 Enter）'))
    btn_select_point.label.set_text(T('取消选点' if selecting_point else '在轨迹上选点'))
    btn_immersive.label.set_text(T('沉浸 √' if immersive else '沉浸 V'))
    btn_lang.label.set_text('EN' if UI_LANG == 'zh' else '中文')
    refresh_task_badges()
    refresh_locators()
    refresh_card()
    refresh_hud()
    refresh_force_analysis()
    refresh_target_band()
    if preview_speed is None:
        preview_text.set_text(T('拖动滑块：亮青色虚线就是「如果现在点火」的轨道'))
        preview_text.set_color(C_CYAN)
    else:
        _set_preview(preview_speed)
    toast('已切换到中文（press L or the EN button for English）' if UI_LANG == 'zh' else 'Switched to English (press L or 中文 to switch back)', 2.8, 'info')
    mark_ui_dirty()
    if not HEADLESS:
        fig.canvas.draw()
        return
    fig.canvas.draw()

def on_key(event):
    if event.name == ' ':
        toggle_pause()
        return
    if event.name == 'enter':
        fire()
        return
    if event.name in ('r', 'R'):
        reset_task(None, keep_view=True)
        return
    if event.name in ('h', 'H'):
        switch_card_page(1 - card_page)
        return
    if event.name in ('f', 'F'):
        toggle_force_analysis()
        return
    if event.name in ('l', 'L'):
        set_ui_language('en' if UI_LANG == 'zh' else 'zh')
        return
    if event.name in ('f11', 'F11'):
        toggle_fullscreen()
        return
    if event.name in ('v', 'V'):
        toggle_immersive()
        return
    if event.name == 'escape':
        if immersive:
            toggle_immersive()

rebuild_ui_rects()
fig.canvas.mpl_connect('scroll_event', on_scroll)
fig.canvas.mpl_connect('button_press_event', on_mouse_press)
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
fig.canvas.mpl_connect('button_release_event', on_mouse_release)
fig.canvas.mpl_connect('resize_event', on_resize)
fig.canvas.mpl_connect('key_press_event', on_key)
_orig_draw_idle = fig.canvas.draw_idle
_orig_draw = fig.canvas.draw

def _patched_draw_idle(*args, **kwargs):
    mark_ui_dirty()
    return _orig_draw_idle(*args, **kwargs)

def _patched_draw(*args, **kwargs):
    mark_ui_dirty()
    return _orig_draw(*args, **kwargs)

fig.canvas.draw_idle = _patched_draw_idle
fig.canvas.draw = _patched_draw
build_dynamic_artists()
switch_card_page(0)
reset_task(0, keep_view=True)
toast(T('现在是任务 1：起始轨道偏椭圆，试着调速度把它修圆（按 H 看讲解）'), 5.0, 'info')
try:
    fig.canvas.manager.set_window_title('宇宙速度探究器 · 课堂版')
except Exception:
    pass
try:
    fig.canvas.toolbar.pack_forget()
except Exception:
    try:
        fig.canvas.toolbar_visible = False
    except Exception:
        pass

def main():
    global simulation_rate, follow_view, paused
    if HEADLESS:
        simulation_rate = RATE_MAX
        report = [f'贴图来源：地球={earth_src or '程序生成（未找到 earth.png）'} 月球={moon_src or '程序生成（未找到 moon.png）'}']
        for idx in range(TASK_COUNT):
            reset_task(idx, keep_view=False)
            run_auto_demo()
            frames = 0
            wall_start = time.perf_counter()
            while frames < 4000 and time.perf_counter() - wall_start < 30.0:
                update(frames)
                frames += 1
                if task_done[idx]:
                    break
            peri, apo, energy, ecc = peri_apo_now()
            checklist = task_checklist()
            detail = ' / '.join(('√' if ok else '○' for _, ok, _ in checklist))
            if idx == 2 and task_phase >= 1:
                r_rel, v_rel, e_rel, ecc_rel, peri_r, apo_r = moon_relative_elements()
                shape = f'环月：高度={r_rel - R_MOON:,.0f}km 近月点={peri_r - R_MOON:,.0f}km e={ecc_rel:.3f}'
                extra = f' 阶段={task_phase} 相对月球ε={e_rel:.4f} v={v_rel:.2f}km/s {shape}'
            else:
                extra = f' 阶段={task_phase}'
            report.append(f'任务{idx + 1} {TASK_NAMES[idx]:<6} e={ecc:.3f} 远地点={'∞' if not np.isfinite(apo) else f'{apo - R_EARTH:>9,.0f}km'} 完成={str(task_done[idx]):<5} 帧={frames:<4} 条件={detail}{extra}')
            continue
        print('\n'.join(report))
        try:
            Path.cwd().joinpath('headless_report.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
        except OSError:
            pass
        simulation_rate = 1.0
        reset_task(1, keep_view=False)
        run_auto_demo()
        update(0)
        switch_card_page(0)
        toast(T('自动演示标准解：这就是界面各区域的真实样子'), 6.0, 'info')
        out_dir = Path.cwd()
        fig.savefig(out_dir / 'preview.png', dpi=110, facecolor=C_SPACE)
        print('preview.png 已生成')
        reset_task(2, keep_view=False)
        fill_recommended_speed()
        update(0)
        switch_card_page(1)
        toast(T('讲解页：为什么用这个速度、合理区间和真实航天任务'), 6.0, 'success')
        fig.savefig(out_dir / 'preview_lesson.png', dpi=110, facecolor=C_SPACE)
        print('preview_lesson.png 已生成')
        reset_task(2, keep_view=False)
        run_auto_demo()
        for _ in range(6):
            update(0)
        toggle_force_analysis()
        update(0)
        toast(T('受力分析：白=合力，蓝/紫=地球/月球引力，虚线=切向(改速率)与法向(改方向)'), 6.0, 'info')
        fig.savefig(out_dir / 'preview_force_toast.png', dpi=110, facecolor=C_SPACE)
        toast_patch.set_visible(False)
        toast_text.set_visible(False)
        update_toast()
        fig.savefig(out_dir / 'preview_force.png', dpi=110, facecolor=C_SPACE)
        print('preview_force.png 已生成')
        simulation_rate = RATE_MAX
        reset_task(2, keep_view=False)
        if show_force_analysis:
            toggle_force_analysis()
        task_done[2] = False
        run_auto_demo()
        for _ in range(4000):
            update(0)
            r_rel, _, e_rel, ecc_rel, _, _ = moon_relative_elements()
            if e_rel < 0 and ecc_rel < 0.15:
                break
        follow_view = False
        for _ in range(90):
            update(0)
            mp_now, _ = moon_position(moon_time)
            apply_view(mp_now[0], mp_now[1], 42000.0)
        paused = True
        switch_card_page(0)
        mp, _ = moon_position(moon_time)
        follow_view = False
        apply_view(mp[0], mp[1], 42000.0)
        refresh_locators()
        refresh_orbit_annotations()
        refresh_prediction(force=True)
        update(0)
        toast(T('任务 3 通关：近月制动被捕获，再在近月点减速修成环月圆轨道'), 6.0, 'success')
        fig.savefig(out_dir / 'preview_lunar_toast.png', dpi=110, facecolor=C_SPACE)
        toast_patch.set_visible(False)
        toast_text.set_visible(False)
        update_toast()
        fig.savefig(out_dir / 'preview_lunar.png', dpi=110, facecolor=C_SPACE)
        print('preview_lunar.png 已生成')
        return
    render_frame(force=True)
    try:
        fig.canvas.manager.window.after(400, maximize_for_projector)
    except Exception:
        pass
    start_animation()
    plt.show()

if __name__ == '__main__':
    main()
