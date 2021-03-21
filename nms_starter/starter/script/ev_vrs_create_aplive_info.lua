local userDomainMoid = ARGV[1]
local confE164 = ARGV[2]
local liveName = ARGV[3]
local liveStartTime = ARGV[4]
local encMode = ARGV[5]

-- 如果存在同名预约直播，删除
local ApLiveInfoKey = "aplive:" .. confE164 .. ":info"
redis.call("DEL", ApLiveInfoKey)
local UserDomainApLiveKey = "domain:" .. userDomainMoid .. ":aplive"
redis.call("SREM", UserDomainApLiveKey, confE164)

-- 添加预约直播
redis.call("SADD", UserDomainApLiveKey, confE164)
redis.call(
    "HMSET",
    ApLiveInfoKey,
    "domain_moid",
    userDomainMoid,
    "conf_e164",
    confE164,
    "live_name",
    liveName,
    "live_start_time",
    liveStartTime,
    "encmode",
    encMode
)
