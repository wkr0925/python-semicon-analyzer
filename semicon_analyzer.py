#!/usr/bin/env python3
"""
鍗婂浣撳櫒浠舵暟鎹垎鏋愬伐鍏?鈥?semicon-analyzer
===========================================

鐢ㄤ簬寰數瀛愪笓涓氬疄楠屾暟鎹殑鑷姩鍖栧垎鏋愪笌鍙鍖栥€?
鍔熻兘:
  - 璇诲彇 CSV/TXT 鏍煎紡鐨勫崐瀵间綋鍣ㄤ欢娴嬮噺鏁版嵁
  - 缁樺埗 MOSFET 杞Щ鐗规€ф洸绾?(Id-Vgs) 鍜岃緭鍑虹壒鎬ф洸绾挎棌 (Id-Vds)
  - 鑷姩鎻愬彇闃堝€肩數鍘?Vth (绾挎€у鎺ㄦ硶)
  - 杈撳嚭绉戠爺绾?SVG 鐭㈤噺鍥? 鍙洿鎺ユ彃鍏ュ疄楠屾姤鍛?
鐢ㄦ硶:
  python semicon_analyzer.py                          # 浜や簰妯″紡
  python semicon_analyzer.py --file data/transfer.csv  # 鎸囧畾鏂囦欢
  python semicon_analyzer.py --demo                    # 浣跨敤鍐呯疆婕旂ず鏁版嵁

渚濊禆: Python 3.8+, numpy, matplotlib
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import argparse
import sys
import os
from pathlib import Path

# 鈹€鈹€ 涓枃瀛椾綋閰嶇疆 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# 鑷姩妫€娴嬬郴缁熶腑鏂囧瓧浣? 纭繚瀹為獙鎶ュ憡涓眽瀛楁甯告樉绀?matplotlib.rcParams['font.sans-serif'] = [
    'SimHei', 'Microsoft YaHei', 'Noto Sans CJK SC',
    'WenQuanYi Micro Hei', 'Arial Unicode MS', 'DejaVu Sans'
]
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['figure.dpi'] = 150
matplotlib.rcParams['savefig.dpi'] = 150
matplotlib.rcParams['savefig.bbox'] = 'tight'


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  鏁版嵁鍔犺浇
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
def load_csv(filepath):
    """
    浠?CSV 鏂囦欢鍔犺浇鍗婂浣撴祴閲忔暟鎹€?
    鏀寔鐨勬牸寮?
      # 娉ㄩ噴琛?(浠?# 寮€澶? 鑷姩璺宠繃)
      Vgs,Id          鈫?杞Щ鐗规€? 鏍呮簮鐢靛帇(V), 婕忔瀬鐢垫祦(A)
      Vds,Id          鈫?杈撳嚭鐗规€? 婕忔簮鐢靛帇(V), 婕忔瀬鐢垫祦(A)
      Vgs,Vds,Id      鈫?涓夊垪鏍煎紡 (鍚缁刅gs鐨勮緭鍑虹壒鎬?

    鍙傛暟:
      filepath: CSV 鏂囦欢璺緞
    杩斿洖:
      data:   numpy 缁撴瀯鍖栨暟缁?(瀛楁鍚嶈嚜鍔ㄤ粠琛ㄥご璇诲彇)
      header: 鍒楀悕鍒楄〃
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"鏂囦欢涓嶅瓨鍦? {filepath}")

    # 璇诲彇鏂囦欢, 璺宠繃娉ㄩ噴琛?    lines = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            lines.append(line)

    if len(lines) < 2:
        raise ValueError(f"鏂囦欢鍐呭涓嶈冻: {filepath} (鑷冲皯闇€瑕佽〃澶?1琛屾暟鎹?")

    # 绗竴琛屼负琛ㄥご
    header = [h.strip() for h in lines[0].split(',')]

    # 鏁版嵁琛?    rows = []
    for line in lines[1:]:
        try:
            rows.append([float(x.strip()) for x in line.split(',')])
        except ValueError:
            continue  # 璺宠繃鏍煎紡閿欒鐨勮

    data = np.array(rows)
    print(f"[鍔犺浇] {filepath}: {len(rows)} 琛? {len(header)} 鍒?{header}")
    return data, header


def load_demo_data():
    """
    鐢熸垚鍐呯疆婕旂ず鏁版嵁 鈥?妯℃嫙涓€涓?n娌熼亾澧炲己鍨?MOSFET 鐨勭壒鎬с€?
    浣跨敤绠€鍖栫殑 MOSFET 妯″瀷:
      绾挎€у尯 (Vds < Vgs-Vth):
        Id = K * [2*(Vgs-Vth)*Vds - Vds虏]
      楗卞拰鍖?(Vds >= Vgs-Vth):
        Id = K * (Vgs-Vth)虏 * (1 + 位*Vds)

    鍙傛暟:
      K   = 0.5 mA/V虏  (璺ㄥ鍙傛暟)
      Vth = 1.0 V      (闃堝€肩數鍘?
      位   = 0.02 V鈦宦?  (娌熼亾闀垮害璋冨埗绯绘暟)
    """
    K, VTH, LAMBDA = 0.5e-3, 1.0, 0.02

    # 鈹€鈹€ 杞Щ鐗规€ф暟鎹?(Vds鍥哄畾=3V, Vgs鎵弿) 鈹€鈹€
    vgs = np.linspace(0, 5, 51)
    vds_fixed = 3.0
    id_transfer = np.zeros_like(vgs)
    for i, vg in enumerate(vgs):
        if vg <= VTH:
            id_transfer[i] = 1e-12  # 浜氶槇鍊? 鏋佸井灏忕數娴?        elif vds_fixed < vg - VTH:
            # 绾挎€у尯
            id_transfer[i] = K * (2*(vg-VTH)*vds_fixed - vds_fixed**2)
        else:
            # 楗卞拰鍖?            id_transfer[i] = K * (vg-VTH)**2 * (1 + LAMBDA*vds_fixed)

    # 鈹€鈹€ 杈撳嚭鐗规€ф暟鎹?(澶氱粍Vgs, Vds鎵弿) 鈹€鈹€
    vgs_values = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    vds = np.linspace(0, 5, 50)
    id_output = {}
    for vg in vgs_values:
        ids = np.zeros_like(vds)
        for j, vd in enumerate(vds):
            if vg <= VTH:
                ids[j] = 1e-12
            elif vd < vg - VTH:
                ids[j] = K * (2*(vg-VTH)*vd - vd**2)
            else:
                ids[j] = K * (vg-VTH)**2 * (1 + LAMBDA*vd)
        id_output[vg] = ids

    return vgs, id_transfer, vds, id_output, VTH


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  闃堝€肩數鍘嬫彁鍙?(绾挎€у鎺ㄦ硶)
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
def extract_vth(vgs, id_data, smooth_window=5):
    """
    浣跨敤绾挎€у鎺ㄦ硶 (Linear Extrapolation) 鎻愬彇 MOSFET 闃堝€肩數鍘嬨€?
    绠楁硶姝ラ:
      1. 瀵?Id-Vgs 鏁版嵁鍋氭粦鍔ㄧ獥鍙ｅ钩婊?      2. 璁＄畻璺ㄥ gm = dId/dVgs
      3. 鎵惧埌 gm 鏈€澶х偣 (鏈€澶ц法瀵肩偣, 鍗虫渶寮哄弽鍨嬬偣)
      4. 杩囪鐐瑰仛鍒囩嚎, 鍒囩嚎涓?Vgs 杞寸殑浜ょ偣 = Vth

    鍙傛暟:
      vgs:           鏍呮簮鐢靛帇鏁扮粍 (V)
      id_data:       婕忔瀬鐢垫祦鏁扮粍 (A)
      smooth_window: 骞虫粦绐楀彛澶у皬 (濂囨暟)
    杩斿洖:
      vth: 闃堝€肩數鍘?(V)
    """
    # 1. 婊戝姩绐楀彛骞虫粦 (鍘婚櫎娴嬮噺鍣０)
    if smooth_window > 2 and len(id_data) > smooth_window:
        kernel = np.ones(smooth_window) / smooth_window
        id_smooth = np.convolve(id_data, kernel, mode='same')
    else:
        id_smooth = id_data.copy()

    # 2. 璁＄畻璺ㄥ gm = dId/dVgs
    gm = np.gradient(id_smooth, vgs)

    # 3. 鎵惧埌 gm 鏈€澶у€煎搴旂殑绱㈠紩
    #    璺宠繃寮€澶村拰缁撳熬 (杈圭晫鏁堝簲)
    start = len(vgs) // 10
    end = len(vgs) - start
    gm_max_idx = start + np.argmax(gm[start:end])

    # 4. 杩囨渶澶ц法瀵肩偣鍋氬垏绾?    slope = gm[gm_max_idx]
    intercept = id_smooth[gm_max_idx] - slope * vgs[gm_max_idx]

    # 5. 鍒囩嚎涓嶸gs杞翠氦鐐?= -intercept/slope
    vth = -intercept / slope

    return vth, gm_max_idx, slope, intercept, gm, id_smooth


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  缁樺浘鍑芥暟
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
def plot_transfer_curve(vgs, id_data, vth=None, gm_idx=None,
                        slope=None, intercept=None,
                        save_path='output/transfer_curve.svg'):
    """
    缁樺埗 MOSFET 杞Щ鐗规€ф洸绾?(Id vs Vgs, 鍗婂鏁板潗鏍?銆?
    鍗婂鏁板潗鏍囧彲浠ュ悓鏃舵竻鏅板睍绀?
      - 浜氶槇鍊煎尯 (Vgs < Vth, Id 鏋佷綆, nA~pA绾?
      - 绾挎€у尯/楗卞拰鍖?(Vgs > Vth, Id 蹇€熶笂鍗?
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))

    # 涓绘洸绾?鈥?鍗婂鏁板潗鏍?    ax.semilogy(vgs, id_data * 1000, 'b-o', markersize=3,
                linewidth=1.2, markerfacecolor='white',
                label='瀹炴祴鏁版嵁 Id (mA)', zorder=2)

    # 濡傛灉鎻愪緵浜哣th鎻愬彇缁撴灉, 缁樺埗澶栨帹绾?    if vth is not None and gm_idx is not None:
        # 闃堝€肩數鍘嬬珫绾?        ax.axvline(x=vth, color='red', linestyle='--', linewidth=1.2,
                   alpha=0.8, label=f'Vth = {vth:.2f} V')
        # 鏈€澶ц法瀵肩偣
        ax.plot(vgs[gm_idx], id_data[gm_idx] * 1000, 'r*',
                markersize=12, markerfacecolor='red',
                label=f'鏈€澶ц法瀵肩偣 (gm={slope*1000:.2f} mS)')
        # 澶栨帹鍒囩嚎
        x_tangent = np.linspace(vth - 0.3, vgs[gm_idx] + 0.5, 50)
        y_tangent = (slope * x_tangent + intercept) * 1000
        # 鍙粯鍒秠>0鐨勯儴鍒?        mask = y_tangent > 1e-6
        ax.semilogy(x_tangent[mask], y_tangent[mask], 'r--',
                    linewidth=1, alpha=0.6, label='澶栨帹鍒囩嚎')

    ax.set_xlabel('鏍呮簮鐢靛帇 Vgs (V)', fontsize=13)
    ax.set_ylabel('婕忔瀬鐢垫祦 Id (mA)', fontsize=13)
    ax.set_title('MOSFET 杞Щ鐗规€ф洸绾?(Transfer Characteristic)', fontsize=14)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim(vgs[0], vgs[-1])

    # 娣诲姞璇存槑鏂囨湰妗?    textstr = (
        f'鍣ㄤ欢绫诲瀷: n娌熼亾澧炲己鍨?MOSFET\n'
        f'娴嬮噺鏉′欢: Vds = 3.0 V (鍥哄畾)'
    )
    if vth is not None:
        textstr += f'\n鎻愬彇 Vth = {vth:.3f} V (绾挎€у鎺ㄦ硶)'
    ax.text(0.98, 0.04, textstr, transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='svg')
    plt.savefig(save_path.replace('.svg', '.png'), format='png', dpi=200)
    print(f"[杈撳嚭] 杞Щ鐗规€ф洸绾? {save_path}")
    plt.close(fig)


def plot_output_curves(vds, id_dict, save_path='output/output_curves.svg'):
    """
    缁樺埗 MOSFET 杈撳嚭鐗规€ф洸绾挎棌 (Id vs Vds, 浠gs涓哄弬鏁?銆?
    姣忔潯鏇茬嚎瀵瑰簲涓€涓浐瀹氱殑 Vgs 鍊? 灞曠ず:
      - 绾挎€у尯: Vds < Vgs-Vth, Id 闅?Vds 绾挎€у闀?      - 楗卞拰鍖? Vds > Vgs-Vth, Id 瓒嬩簬鎭掑畾 (鐣ユ湁涓婄繕 鈫?娌熼暱璋冨埗鏁堝簲)
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))

    # 鐢熸垚棰滆壊娓愬彉
    n_curves = len(id_dict)
    colors = plt.cm.plasma(np.linspace(0.05, 0.95, n_curves))

    for idx, (vgs_val, id_data) in enumerate(id_dict.items()):
        label = f'Vgs = {vgs_val:.1f} V'
        ax.plot(vds, id_data * 1000, '-', color=colors[idx],
                linewidth=1.8, label=label, marker='.', markersize=2)

    ax.set_xlabel('婕忔簮鐢靛帇 Vds (V)', fontsize=13)
    ax.set_ylabel('婕忔瀬鐢垫祦 Id (mA)', fontsize=13)
    ax.set_title('MOSFET 杈撳嚭鐗规€ф洸绾挎棌 (Output Characteristics)', fontsize=14)
    ax.legend(fontsize=9, loc='lower right', ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(vds[0], vds[-1])

    # 鏍囨敞绾挎€у尯鍜岄ケ鍜屽尯 (绀烘剰)
    ax.annotate('绾挎€у尯\n(Linear)', xy=(0.3, 0.25), xycoords='axes fraction',
                fontsize=10, color='gray', ha='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    ax.annotate('楗卞拰鍖篭n(Saturation)', xy=(0.75, 0.6), xycoords='axes fraction',
                fontsize=10, color='gray', ha='center',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='svg')
    plt.savefig(save_path.replace('.svg', '.png'), format='png', dpi=200)
    print(f"[杈撳嚭] 杈撳嚭鐗规€ф洸绾? {save_path}")
    plt.close(fig)


def plot_gm_curve(vgs, gm, id_smooth, save_path='output/transconductance.svg'):
    """
    缁樺埗璺ㄥ gm 闅?Vgs 鐨勫彉鍖栨洸绾裤€?
    璺ㄥ gm = dId/dVgs, 鍙嶆槧浜?MOSFET 鐨勬斁澶ц兘鍔涖€?    鏈€澶ц法瀵肩偣鏄嚎鎬у鎺ㄦ硶鎻愬彇 Vth 鐨勫叧閿弬鑰冪偣銆?    """
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    # gm 鏇茬嚎
    ax1.plot(vgs, gm * 1000, 'b-', linewidth=1.5, label='璺ㄥ gm (mS)')
    ax1.set_xlabel('鏍呮簮鐢靛帇 Vgs (V)', fontsize=13)
    ax1.set_ylabel('璺ㄥ gm (mS)', fontsize=13, color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True, alpha=0.3)

    # Id 鏇茬嚎 (鍙宠酱, 瀵规暟)
    ax2.semilogy(vgs, id_smooth * 1000, 'r--', linewidth=1,
                 alpha=0.5, label='Id (mA) - 瀵规暟鍧愭爣')
    ax2.set_ylabel('婕忔瀬鐢垫祦 Id (mA)', fontsize=13, color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # 鏍囨敞鏈€澶ц法瀵肩偣
    gm_max_idx = np.argmax(gm)
    ax1.plot(vgs[gm_max_idx], gm[gm_max_idx] * 1000, 'r*',
             markersize=12, label=f'gm_max = {gm[gm_max_idx]*1000:.2f} mS')

    ax1.set_title('璺ㄥ鏇茬嚎 (Transconductance)', fontsize=14)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='svg')
    print(f"[杈撳嚭] 璺ㄥ鏇茬嚎: {save_path}")
    plt.close(fig)


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  缁撴灉杈撳嚭
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
def print_parameters(vth, gm_max, gm_idx, vgs):
    """鎵撳嵃鎻愬彇鐨勫櫒浠跺弬鏁?""
    print("\n" + "=" * 50)
    print("  Semiconductor Device Parameter Report")
    print("=" * 50)
    print(f"  Device Type:     n-channel enhancement MOSFET")
    print(f"  Threshold Vth:   {vth:.4f} V")
    print(f"  Max gm:          {gm_max*1000:.3f} mS")
    print(f"  Vgs at max gm:   {vgs[gm_idx]:.3f} V")
    print(f"  Method:          Linear Extrapolation")
    print("=" * 50)


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?#  涓诲叆鍙?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
def main():
    parser = argparse.ArgumentParser(
        description='鍗婂浣撳櫒浠舵暟鎹垎鏋愬伐鍏?鈥?MOSFET 鐗规€у垎鏋愪笌鍙鍖?,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
绀轰緥:
  %(prog)s                     浜や簰妯″紡 (浣跨敤鍐呯疆婕旂ず鏁版嵁)
  %(prog)s --demo              浣跨敤鍐呯疆婕旂ず鏁版嵁
  %(prog)s -f data/transfer.csv  鍒嗘瀽 CSV 鏁版嵁鏂囦欢
        """
    )
    parser.add_argument('-f', '--file', type=str,
                        help='CSV 鏁版嵁鏂囦欢璺緞')
    parser.add_argument('--demo', action='store_true',
                        help='浣跨敤鍐呯疆婕旂ず鏁版嵁 (n娌熼亾澧炲己鍨婱OSFET)')
    parser.add_argument('-o', '--output', type=str, default='output',
                        help='鍥剧墖杈撳嚭鐩綍 (榛樿: output/)')

    args = parser.parse_args()

    print("=" * 50)
    print("  Semiconductor Device Analyzer v1.0")
    print("  MOSFET Characteristic Analysis Tool")
    print("=" * 50)
    print()

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    # 鈹€鈹€ 鍔犺浇鏁版嵁 鈹€鈹€
    if args.file:
        # 浠庢枃浠跺姞杞?        data, header = load_csv(args.file)
        if data.shape[1] >= 3:
            print("\n鈿?妫€娴嬪埌3鍒椾互涓婃暟鎹? 浣跨敤绗?鍒?Vgs, 绗?鍒?Id")
        vgs = data[:, 0]
        id_data = data[:, 1]
        # 瀵逛簬鏂囦欢鏁版嵁, 鐢熸垚绠€鍖栫殑杈撳嚭鏇茬嚎
        vds_demo = np.linspace(0, 5, 50)
        id_output_demo = {}
        for vg in [1.5, 2.0, 2.5, 3.0]:
            id_output_demo[vg] = np.clip(
                0.5e-3 * (vg - 1.0)**2 * (1 + 0.02 * vds_demo), 0, None
            )
    else:
        # 浣跨敤婕旂ず鏁版嵁
        print("[婕旂ず] 浣跨敤鍐呯疆 n娌熼亾澧炲己鍨?MOSFET 妯″瀷鏁版嵁\n")
        vgs, id_data, vds_demo, id_output_demo, _ = load_demo_data()

    # 鈹€鈹€ 1. 鎻愬彇闃堝€肩數鍘?鈹€鈹€
    print("\n[1/4] 鎻愬彇闃堝€肩數鍘?Vth (绾挎€у鎺ㄦ硶)...")
    vth, gm_idx, slope, intercept, gm, id_smooth = extract_vth(vgs, id_data)
    gm_max = gm[gm_idx]
    print_parameters(vth, gm_max, gm_idx, vgs)

    # 鈹€鈹€ 2. 缁樺埗杞Щ鐗规€ф洸绾?鈹€鈹€
    print("\n[2/4] 缁樺埗杞Щ鐗规€ф洸绾?..")
    plot_transfer_curve(vgs, id_data, vth, gm_idx, slope, intercept,
                        save_path=f'{output_dir}/transfer_curve.svg')

    # 鈹€鈹€ 3. 缁樺埗杈撳嚭鐗规€ф洸绾?鈹€鈹€
    print("\n[3/4] 缁樺埗杈撳嚭鐗规€ф洸绾挎棌...")
    plot_output_curves(vds_demo, id_output_demo,
                       save_path=f'{output_dir}/output_curves.svg')

    # 鈹€鈹€ 4. 缁樺埗璺ㄥ鏇茬嚎 鈹€鈹€
    print("\n[4/4] 缁樺埗璺ㄥ鏇茬嚎...")
    plot_gm_curve(vgs, gm, id_smooth,
                  save_path=f'{output_dir}/transconductance.svg')

    # 鈹€鈹€ 瀹屾垚 鈹€鈹€
    print(f"\n{'='*50}")
    print(f"  [OK] Analysis complete! 3 plots generated")
    print(f"  [>>] Output: {os.path.abspath(output_dir)}/")
    print(f"  [>>] Ready for lab report or paper")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    # Fix Windows GBK encoding for emoji/special chars
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    main()
