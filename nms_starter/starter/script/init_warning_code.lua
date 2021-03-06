-- 初始化告警码表 固定值
redis.call(
    "HMSET",
    "warning:code:1003",
    "type",
    "终端设备告警",
    "name",
    "丢包率过高(5%)",
    "level",
    "normal",
    "description",
    "终端接收丢包率超过5%",
    "suggestion",
    "1.检查终端侧网络状况是否异常;2.建议客户降低呼叫码率."
)
redis.call(
    "HMSET",
    "warning:code:1004",
    "type",
    "终端设备告警",
    "name",
    "丢包率过高(10%)",
    "level",
    "important",
    "description",
    "终端接收丢包率超过10%",
    "suggestion",
    "1.检查终端侧网络状况是否异常;2.建议客户降低呼叫码率."
)
redis.call(
    "HMSET",
    "warning:code:1006",
    "type",
    "终端设备告警",
    "name",
    "注册GK失败",
    "level",
    "critical",
    "description",
    "注册GK失败",
    "suggestion",
    "1.检查终端侧网络状况是否异常;2.确认E164号码是否冲突;3.确认密码是否正确;4.确认是否超出授权范围."
)
redis.call(
    "HMSET",
    "warning:code:1007",
    "type",
    "终端设备告警",
    "name",
    "版本过低",
    "level",
    "important",
    "description",
    "终端版本非推荐版本(最新版本)",
    "suggestion",
    "建议客户升级版本"
)
redis.call(
    "HMSET",
    "warning:code:1008",
    "type",
    "终端设备告警",
    "name",
    "终端异常重启",
    "level",
    "critical",
    "description",
    "终端异常重启",
    "suggestion",
    "终端进程崩溃导致异常重启,需要提供崩溃日志"
)
redis.call(
    "HMSET",
    "warning:code:1019",
    "type",
    "终端设备告警",
    "name",
    "E1全1线路故障",
    "level",
    "critical",
    "description",
    "E1全1，将导致线路无法使用",
    "suggestion",
    "建议检查E1线缆是否存在问题"
)
redis.call(
    "HMSET",
    "warning:code:1020",
    "type",
    "终端设备告警",
    "name",
    "E1失同步线路故障",
    "level",
    "critical",
    "description",
    "E1失同步，将导致线路无法使用",
    "suggestion",
    "建议检查E1线缆是否存在问题"
)
redis.call(
    "HMSET",
    "warning:code:1021",
    "type",
    "终端设备告警",
    "name",
    "E1远端告警线路故障",
    "level",
    "critical",
    "description",
    "E1远端告警，远端设备存在告警，将导致线路无法正常使用",
    "suggestion",
    "建议检查E1线缆是否存在问题"
)
redis.call(
    "HMSET",
    "warning:code:1022",
    "type",
    "终端设备告警",
    "name",
    "E1失载波线路故障",
    "level",
    "normal",
    "description",
    "E1失载波，将导致线路无法使用",
    "suggestion",
    "建议检查E1线缆是否存在问题"
)
redis.call(
    "HMSET",
    "warning:code:1023",
    "type",
    "终端设备告警",
    "name",
    "终端CPU资源占用率过高",
    "level",
    "critical",
    "description",
    "设备CPU占用率过高（5分钟内平均单核占用率高于阈值），资源不足，将导致系统无法正常响应",
    "suggestion",
    "建议重启设备恢复"
)
redis.call(
    "HMSET",
    "warning:code:1024",
    "type",
    "终端设备告警",
    "name",
    "终端内存资源占用率过高",
    "level",
    "critical",
    "description",
    "设备内存占用率过高（5分钟内平均内存占用率高于阈值），资源不足，将导致系统无法正常响应",
    "suggestion",
    "建议重启设备恢复"
)
redis.call(
    "HMSET",
    "warning:code:2002",
    "type",
    "服务器设备告警",
    "name",
    "cpu高于阈值",
    "level",
    "critical",
    "description",
    "服务器单核cpu5分钟内平均占用率超过阈值",
    "suggestion",
    "1.网口是否遭遇网络风暴;2.负载过高,超过服务器阈值;3.软硬件是否存在异常.",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2003",
    "type",
    "服务器设备告警",
    "name",
    "内存高于阈值",
    "level",
    "critical",
    "description",
    "服务器内存5分钟内平均使用率超过阈值",
    "suggestion",
    "1.网口是否遭遇网络风暴;2.负载过高,超过服务器阈值;3.软硬件是否存在异常.",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2004",
    "type",
    "服务器设备告警",
    "name",
    "NTP时间同步失败",
    "level",
    "important",
    "description",
    "服务器同步NTP时间失败",
    "suggestion",
    "1.可能导致系统时间不一致;2.建议排查网络"
)
redis.call(
    "HMSET",
    "warning:code:2005",
    "type",
    "服务器设备告警",
    "name",
    "PAS接入容量超过阈值",
    "level",
    "important",
    "description",
    "单台PAS的接入容量超过阈值",
    "suggestion",
    "新增用户建议分载在其他CSU服务器",
    "unit",
    "个"
)
redis.call(
    "HMSET",
    "warning:code:2006",
    "type",
    "服务器设备告警",
    "name",
    "并发呼叫容量超过阈值",
    "level",
    "important",
    "description",
    "单台PAS的呼叫对数量超过阈值",
    "suggestion",
    "建议新增MTS服务器进行均衡负载",
    "unit",
    "对"
)
redis.call(
    "HMSET",
    "warning:code:2007",
    "type",
    "服务器设备告警",
    "name",
    "端口资源使用百分比超过阈值",
    "level",
    "important",
    "description",
    "端口资源使用率超过阈值(百分比超阈值)",
    "suggestion",
    "1.建议新增mediaresource服务器;2.检查客户行为是否长期占用不释放.",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2011",
    "type",
    "服务器设备告警",
    "name",
    "服务器异常",
    "level",
    "critical",
    "description",
    "服务器进程崩溃",
    "suggestion",
    "查看服务器log日志"
)
redis.call(
    "HMSET",
    "warning:code:2013",
    "type",
    "服务器设备告警",
    "name",
    "接收丢包(5%)",
    "level",
    "normal",
    "description",
    "物理服务器接收码流丢包率超过5%",
    "suggestion",
    ""
)
redis.call(
    "HMSET",
    "warning:code:2014",
    "type",
    "服务器设备告警",
    "name",
    "接收丢包(10%)",
    "level",
    "normal",
    "description",
    "物理服务器接收码流丢包率超过10%",
    "suggestion",
    ""
)
redis.call(
    "HMSET",
    "warning:code:2015",
    "type",
    "服务器设备告警",
    "name",
    "服务器下线",
    "level",
    "critical",
    "description",
    "服务器下线",
    "suggestion",
    "查看日志文件确认是否人为重启",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2016",
    "type",
    "服务器设备告警",
    "name",
    "网管收集器接入容量超过阈值",
    "level",
    "critical",
    "description",
    "单台收集器的设备接入数量超过阈值",
    "suggestion",
    "新增用户建议,分载在其他NMA服务器",
    "unit",
    "个"
)
redis.call(
    "HMSET",
    "warning:code:2018",
    "type",
    "服务器设备告警",
    "name",
    "磁盘空间不足",
    "level",
    "critical",
    "description",
    "设备磁盘剩余空间不足(占用率超阈值),将导致系统无法正常响应",
    "suggestion",
    "建议备份数据后，清理磁盘",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2019",
    "type",
    "服务器设备告警",
    "name",
    "网卡流量过载",
    "level",
    "critical",
    "description",
    "网卡的吞吐量超阈值",
    "suggestion",
    "1.当前并发呼叫过多导致网口吞吐量过载;2.网络可能存在风暴或有攻击行为,导致网口吞吐量过载.",
    "unit",
    "Kbps"
)
redis.call(
    "HMSET",
    "warning:code:2020",
    "type",
    "服务器设备告警",
    "name",
    "MODB同步失败",
    "level",
    "critical",
    "description",
    "MODB同步失败",
    "suggestion",
    "建议检查物理连接线路"
)
redis.call(
    "HMSET",
    "warning:code:2021",
    "type",
    "服务器设备告警",
    "name",
    "服务器切换",
    "level",
    "critical",
    "description",
    "服务器异常导致主备切换",
    "suggestion",
    "建议检查主机状态"
)
redis.call(
    "HMSET",
    "warning:code:2022",
    "type",
    "服务器设备告警",
    "name",
    "服务器切换超时",
    "level",
    "critical",
    "description",
    "keepalive切换超时",
    "suggestion",
    "建议检查主机状态"
)
redis.call(
    "HMSET",
    "warning:code:2023",
    "type",
    "服务器设备告警",
    "name",
    "daemon进程异常",
    "level",
    "critical",
    "description",
    "daemon进程不在",
    "suggestion",
    "建议重启或者手动启动此进程"
)
redis.call(
    "HMSET",
    "warning:code:2024",
    "type",
    "服务器设备告警",
    "name",
    "备机业务异常",
    "level",
    "critical",
    "description",
    "备机业务异常启动，导致主备业务冲突",
    "suggestion",
    "建议检查主备机服务器是否异常"
)
redis.call(
    "HMSET",
    "warning:code:2025",
    "type",
    "服务器设备告警",
    "name",
    "混音器资源使用百分比超过阈值",
    "level",
    "important",
    "description",
    "混音器资源使用率超过阈值(百分比超阈值)",
    "suggestion",
    "1.建议新增扩容服务器;2.检查客户行为是否长期占用不释放.",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2026",
    "type",
    "服务器设备告警",
    "name",
    "合成器资源使用百分比超过阈值",
    "level",
    "important",
    "description",
    "画面合成器资源使用率超过阈值(百分比超阈值)",
    "suggestion",
    "1.建议新增扩容服务器;2.检查客户行为是否长期占用不释放.",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:2027",
    "type",
    "服务器设备告警",
    "name",
    "SA进程异常",
    "level",
    "critical",
    "description",
    "SA进程不存在",
    "suggestion",
    "建议重启或者手动启用此进程."
)
redis.call(
    "HMSET",
    "warning:code:2028",
    "type",
    "服务器设备告警",
    "name",
    "MYSQL主从同步失败",
    "level",
    "critical",
    "description",
    "检测到主从MYSQL之间同步失败",
    "suggestion",
    "建议检查主机状态."
)
redis.call(
    "HMSET",
    "warning:code:2029",
    "type",
    "服务器设备告警",
    "name",
    "网络IP地址冲突",
    "level",
    "critical",
    "description",
    "服务器网络IP地址和其他服务器冲突",
    "suggestion",
    "1. 建议检查服务器IP地址"
)
redis.call(
    "HMSET",
    "warning:code:2030",
    "type",
    "服务器设备告警",
    "name",
    "电视墙板卡服务器温度过高",
    "level",
    "critical",
    "description",
    "电视墙板卡温度超过阈值",
    "suggestion",
    "1.建议检查机框风扇状态;2.建议手动重启板卡."
)
redis.call(
    "HMSET",
    "warning:code:2031",
    "type",
    "服务器设备告警",
    "name",
    "DS系统转发优化未配置",
    "level",
    "critical",
    "description",
    "DataSwitch系统转发优化未配置",
    "suggestion",
    "1.建议联系运维人员处理."
)
redis.call(
    "HMSET",
    "warning:code:2032",
    "type",
    "服务器设备告警",
    "name",
    "云平台主备业务锁异常",
    "level",
    "critical",
    "description",
    "云平台主备业务锁异常",
    "suggestion",
    "1.建议联系运维人员处理."
)
redis.call(
    "HMSET",
    "warning:code:2033",
    "type",
    "服务器设备告警",
    "name",
    "网管收集器进程崩溃",
    "level",
    "critical",
    "description",
    "网管collecter收集器进程崩溃",
    "suggestion",
    "1.建议检查服务器网络状态."
)
redis.call(
    "HMSET",
    "warning:code:2034",
    "type",
    "服务器设备告警",
    "name",
    "dataswitch丢包率过高",
    "level",
    "critical",
    "description",
    "dataswitch丢包率超过5%",
    "suggestion",
    "1.检查物理服务器网口状态是否异常;2.检查服务器转发模块之间的网络状况是否异常."
)
redis.call(
    "HMSET",
    "warning:code:2035",
    "type",
    "服务器设备告警",
    "name",
    "dataswitch丢包率过高",
    "level",
    "critical",
    "description",
    "dataswitch丢包率超过10%",
    "suggestion",
    "1.检查物理服务器网口状态是否异常;2.检查服务器转发模块之间的网络状况是否异常."
)
redis.call(
    "HMSET",
    "warning:code:2036",
    "type",
    "服务器设备告警",
    "name",
    "SM1算法自测试失败",
    "level",
    "critical",
    "description",
    "SM1算法自测试失败",
    "suggestion",
    "1.请确认加密卡是否插好."
)
redis.call(
    "HMSET",
    "warning:code:2037",
    "type",
    "服务器设备告警",
    "name",
    "SM2算法自测试失败",
    "level",
    "critical",
    "description",
    "SM2算法自测试失败",
    "suggestion",
    "1.请确认加密卡是否插好."
)
redis.call(
    "HMSET",
    "warning:code:2038",
    "type",
    "服务器设备告警",
    "name",
    "SM3算法自测试失败",
    "level",
    "critical",
    "description",
    "SM3算法自测试失败",
    "suggestion",
    "1.请联系系统管理员."
)
redis.call(
    "HMSET",
    "warning:code:2039",
    "type",
    "服务器设备告警",
    "name",
    "SM4算法自测试失败",
    "level",
    "critical",
    "description",
    "SM4算法自测试失败",
    "suggestion",
    "1.请联系系统管理员."
)
redis.call(
    "HMSET",
    "warning:code:2040",
    "type",
    "服务器设备告警",
    "name",
    "随机数自测试失败",
    "level",
    "critical",
    "description",
    "随机数自测试失败",
    "suggestion",
    "1.请确认加密卡是否插好."
)
redis.call(
    "HMSET",
    "warning:code:2041",
    "type",
    "服务器设备告警",
    "name",
    "软件完整性自测试失败",
    "level",
    "critical",
    "description",
    "软件完整性自测试失败",
    "suggestion",
    "1.请确认软件是否被修改."
)
redis.call(
    "HMSET",
    "warning:code:2042",
    "type",
    "服务器设备告警",
    "name",
    "随机数生成失败",
    "level",
    "critical",
    "description",
    "随机数生成失败",
    "suggestion",
    "1.请确认加密卡是否插好."
)
redis.call(
    "HMSET",
    "warning:code:2043",
    "type",
    "服务器设备告警",
    "name",
    "U盘备份功能失败",
    "level",
    "important",
    "description",
    "U盘备份功能失败",
    "suggestion",
    "1.请确认备份U盘是否插好."
)
redis.call(
    "HMSET",
    "warning:code:2044",
    "type",
    "服务器设备告警",
    "name",
    "系统未检测到U盘",
    "level",
    "important",
    "description",
    "系统未检测到U盘,会影响系统正常使用,请插入U盘.",
    "suggestion",
    "建议查看服务器的U盘是否正确安装或者是否存在松动导致系统异常."
)
redis.call(
    "HMSET",
    "warning:code:2045",
    "type",
    "服务器设备告警",
    "name",
    "服务器硬盘使用寿命不足",
    "level",
    "critical",
    "description",
    "当前服务器的硬盘使用寿命不足",
    "suggestion",
    "建议尽快联系管理员或者更换设备硬盘"
)
redis.call(
    "HMSET",
    "warning:code:2046",
    "type",
    "服务器设备告警",
    "name",
    "转发服务器流量超阈值",
    "level",
    "critical",
    "description",
    "当前转发服务器的流量超阈值",
    "suggestion",
    "服务器性能可能已达到最大值,需要增加转发服务器,请尽快联系系统管理员"
)
redis.call(
    "HMSET",
    "warning:code:2047",
    "type",
    "服务器设备告警",
    "name",
    "磁盘写入数据超阈值",
    "level",
    "critical",
    "description",
    "当前服务器磁盘写入数据异常",
    "suggestion",
    "建议尽快联系管理员，查看业务状态是否正常，日志状态是否异常"
)
redis.call(
    "HMSET",
    "warning:code:2065",
    "type",
    "服务器设备告警",
    "name",
    "License授权日期小于30天",
    "level",
    "critical",
    "description",
    "License授权即将在30天内到期",
    "suggestion",
    "1.检查服务器中的授权文件是否即将过期 2.建议尽快购买授权避免License到期影响功能使用"
)
redis.call(
    "HMSET",
    "warning:code:2066",
    "type",
    "服务器设备告警",
    "name",
    "License授权日期小于7天",
    "level",
    "important",
    "description",
    "License授权即将在7天内到期",
    "suggestion",
    "1.检查服务器中的授权文件是否即将过期 2.建议尽快购买授权避免License到期影响功能使用"
)
redis.call(
    "HMSET",
    "warning:code:3001",
    "type",
    "MCU告警",
    "name",
    "多电源板异常",
    "level",
    "critical",
    "description",
    "多个电源板故障或未插入机框",
    "suggestion",
    "建议检查电源板是否插紧"
)
redis.call(
    "HMSET",
    "warning:code:3002",
    "type",
    "MCU告警",
    "name",
    "单电源板异常",
    "level",
    "important",
    "description",
    "单个电源板故障或未插入机框",
    "suggestion",
    "建议检查电源板是否插紧"
)
redis.call(
    "HMSET",
    "warning:code:3003",
    "type",
    "MCU告警",
    "name",
    "机箱风扇异常",
    "level",
    "critical",
    "description",
    "风扇故障,转速过低,将影响CPU的正常工作",
    "suggestion",
    "建议进行除尘处理,检查供电线路"
)
redis.call(
    "HMSET",
    "warning:code:3004",
    "type",
    "MCU告警",
    "name",
    "单板温度过高(严重)",
    "level",
    "critical",
    "description",
    "单板温度过高,将影响业务功能的正常运行",
    "suggestion",
    "建议检查机框电源周围环境是否存在热源,是否风扇异常或灰尘,长年运行情况下,定期断电冷却后启动恢复"
)
redis.call(
    "HMSET",
    "warning:code:3005",
    "type",
    "MCU告警",
    "name",
    "单板温度过高(重要)",
    "level",
    "important",
    "description",
    "单板温度过高,将影响业务功能的正常运行",
    "suggestion",
    "建议检查机框电源周围环境是否存在热源,是否风扇异常或灰尘,长年运行情况下,定期断电冷却后启动恢复"
)
redis.call(
    "HMSET",
    "warning:code:3006",
    "type",
    "MCU告警",
    "name",
    "单板温度过高(一般)",
    "level",
    "normal",
    "description",
    "单板温度过高,将影响业务功能的正常运行",
    "suggestion",
    "建议检查机框电源周围环境是否存在热源,是否风扇异常或灰尘,长年运行情况下,定期断电冷却后启动恢复"
)
redis.call(
    "HMSET",
    "warning:code:3007",
    "type",
    "MCU告警",
    "name",
    "单板CPU资源占用率过高",
    "level",
    "critical",
    "description",
    "设备CPU占用率过高(5分钟内平均单核占用率高于阈值),资源不足,将导致系统无法正常响应",
    "suggestion",
    "建议重启设备恢复",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:3008",
    "type",
    "MCU告警",
    "name",
    "单板内存资源占用率过高",
    "level",
    "critical",
    "description",
    "设备内存占用率过高(5分钟内平均内存占用率高于阈值),资源不足,将导致系统无法正常响应",
    "suggestion",
    "建议重启设备恢复",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:3009",
    "type",
    "MCU告警",
    "name",
    "磁盘空间不足",
    "level",
    "critical",
    "description",
    "设备磁盘剩余空间不足(占用率超阈值),将导致系统无法正常响应",
    "suggestion",
    "建议备份数据后,清理磁盘",
    "unit",
    "%"
)
redis.call(
    "HMSET",
    "warning:code:3010",
    "type",
    "MCU告警",
    "name",
    "单板服务器下线",
    "level",
    "critical",
    "description",
    "单板服务器下线",
    "suggestion",
    "查看日志文件确认是否认为重启"
)
redis.call(
    "HMSET",
    "warning:code:3011",
    "type",
    "MCU告警",
    "name",
    "单板电压不在正常范围(严重)",
    "level",
    "critical",
    "description",
    "设备电压不在正常范围，将导致系统故障",
    "suggestion",
    "建议重启设备恢复"
)
redis.call(
    "HMSET",
    "warning:code:3012",
    "type",
    "MCU告警",
    "name",
    "单板电压不在正常范围(重要)",
    "level",
    "important",
    "description",
    "设备电压不在正常范围，将导致系统故障",
    "suggestion",
    "建议重启设备恢复"
)
redis.call(
    "HMSET",
    "warning:code:3013",
    "type",
    "MCU告警",
    "name",
    "单板电压不在正常范围(一般)",
    "level",
    "normal",
    "description",
    "设备电压不在正常范围，将导致系统故障",
    "suggestion",
    "建议重启设备恢复"
)
redis.call(
    "HMSET",
    "warning:code:3014",
    "type",
    "MCU告警",
    "name",
    "单板媒体芯片故障",
    "level",
    "critical",
    "description",
    "单板媒体芯片故障，将导致系统无法正常响应",
    "suggestion",
    "建议重启设备恢复"
)
redis.call(
    "HMSET",
    "warning:code:4001",
    "type",
    "其他",
    "name",
    "智能插座已达最大使用寿命",
    "level",
    "important",
    "description",
    "终端会场中的智能插座已达到最大使用寿命，请更换",
    "suggestion",
    "请更换新的智能插座并重新与中控设备进行配对"
)
redis.call(
    "HMSET",
    "warning:code:4002",
    "type",
    "其他",
    "name",
    "智能插座离线",
    "level",
    "critical",
    "description",
    "终端会场中的智能插座离线",
    "suggestion",
    "1.请确认智能中控主机的SSID名称是否修改,如果有改动,则重新初始化智能插座并配对。2.请确认中控主机的无线热点是否稳定,如不稳定则请更换中控主机。3.请重新初始化智能插座,并进行配对;如果此措施无效,请更换智能插座"
)
