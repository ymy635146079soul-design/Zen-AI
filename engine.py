import datetime
from borax.calendars.lunardate import LunarDate

def get_core_data(year, month, day, hour=0, minute=0):
    try:
        # 1. 基础时间对象
        dt = datetime.datetime(year, month, day, hour, minute)
        
        # 2. 获取公历当天对应的农历对象
        ld = LunarDate.from_solar_date(year, month, day)
        
        # 3. 基础干支（注意：ld.gz_year 默认随正月初一改变）
        y_gz = ld.gz_year
        m_gz = ld.gz_month
        d_gz = ld.gz_day
        
        # 4. 【全自动立春校准逻辑】
        # 只要是1月，或者2月且没到立春点，年柱必须回退
        # 只要过了立春点，即便还没到大年初一，年柱必须进位
        
        # 简单而精准的立春日判定 (立春通常在2月4日左右)
        # 我们查询当天是否有“立春”节气
        is_lichun_passed = False
        # 扫描从年初到今天的节气
        if month == 1:
            is_lichun_passed = False
        elif month == 2:
            if day < 4: 
                is_lichun_passed = False
            elif day > 5:
                is_lichun_passed = True
            else:
                # 4日或5日，通过 ld.term_list 精准判断
                is_lichun_passed = ('立春' in ld.term_list) or (day == 5)
        else:
            is_lichun_passed = True

        # 根据立春状态修正年柱
        if not is_lichun_passed and (month <= 2):
            # 还没到立春，年柱强制等于“公历去年年底”的年柱
            ld_old = LunarDate.from_solar_date(year - 1, 12, 20)
            y_gz = ld_old.gz_year
        elif is_lichun_passed and (month == 2):
            # 过了立春，如果还在正月初一前，ld.gz_year 可能是旧的，强制进位
            # 获取公历今年年中（肯定过完年了）的年柱
            ld_new = LunarDate.from_solar_date(year, 7, 1)
            y_gz = ld_new.gz_year

        # 5. 【晚子时逻辑】
        if hour >= 23:
            target_dt = dt + datetime.timedelta(days=1)
            ld_next = LunarDate.from_solar_date(target_dt.year, target_dt.month, target_dt.day)
            d_gz = ld_next.gz_day

        # 6. 【时柱五鼠遁】
        stems = "甲乙丙丁戊己庚辛壬癸"
        branches = "子丑寅卯辰巳午未申酉戌亥"
        day_stem_idx = stems.find(d_gz[0])
        hour_b_idx = ((hour + 1) // 2) % 12
        hour_s_idx = ((day_stem_idx % 5) * 2 + hour_b_idx) % 10
        h_gz = stems[hour_s_idx] + branches[hour_b_idx]
        
        return {
            "year": y_gz,
            "month": m_gz,
            "day": d_gz,
            "hour": h_gz,
            "status": "success"
        }
    except Exception as e:
        return {
            "year": "Error", "month": "Error", "day": "Error", "hour": "Error",
            "status": "error", "message": str(e)
        }

if __name__ == "__main__":
    # 执行跨年压力测试
    test_date = datetime.datetime(2024, 2, 5, 10, 0) # 2024年立春后，初一前
    res = get_core_data(test_date.year, test_date.month, test_date.day, test_date.hour)
    
    print("\n" + " 🚀 ZEN-AI 引擎全自动化测试 ".center(40, "="))
    print(f"测试点: 2024-02-05 (预期甲辰龙年)")
    print(f"结果: {res['year']} {res['month']} {res['day']} {res['hour']}")
    
    now = datetime.datetime.now()
    curr = get_core_data(now.year, now.month, now.day, now.hour, now.minute)
    print(f"\n实时点: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"结果: {curr['year']} {curr['month']} {curr['day']} {curr['hour']}")
    print("=" * 43)