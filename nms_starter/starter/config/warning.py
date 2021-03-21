# 机框告警码定义
SMU_ALAM_CODE_POWER = 5001  # 电源板异常
SMU_ALAM_CODE_FANSPEED = 5002  # 机箱风扇异常
SMU_ALAM_CODE_TEMPERATURE = 5003  # 单板单板温度过高
SMU_ALAM_CODE_VOLTAGE = 5004  # 单板电压不在正常范围
SMU_ALAM_CODE_CHIP_FAULT = 5005  # 单板媒体芯片故障
SMU_ALAM_CODE_TVS4000_TEMPERATURE = 2030  # 电视墙板卡单板温度超过阈值(严重)

# 告警等级
SMU_ALAM_LV_NOMAL = 0  # 普通告警
SMU_ALAM_LV_IMPORTANT = 1  # 重要告警
SMU_ALAM_LV_CRITICAL = 2  # 严重告警


def smu_warning_code_2_nms(smu_code, level):
    if smu_code == SMU_ALAM_CODE_POWER:
        code = [3002, 3002, 3001][level]
    elif smu_code == SMU_ALAM_CODE_FANSPEED:
        code = 3003
    elif smu_code == SMU_ALAM_CODE_TEMPERATURE:
        code = [3006, 3005, 3004][level]
    elif smu_code == SMU_ALAM_CODE_VOLTAGE:
        code = [3013, 3012, 3011][level]
    elif smu_code == SMU_ALAM_CODE_CHIP_FAULT:
        code = 3014
    elif smu_code == SMU_ALAM_CODE_TVS4000_TEMPERATURE:
        code = 2030
    return code


WARNING_MQ_CONFIG = {
    'mail': ('service.email.ex', 'service.email.k'),
    'wechat': ('wps.notify.ex', '')
}
