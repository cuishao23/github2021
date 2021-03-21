-- 初始化所有域的公共告警设置
-- 参数: s_pas, s_callpair, s_nms, s_media_resource
local s_pas = ARGV[1]
local s_callpair = ARGV[2]
local s_nms = ARGV[3]
local s_media_resource = ARGV[4]

local warningLimitGlobalKey = "warning:limit:global"

redis.call(
    "HMSET",
    warningLimitGlobalKey,
    "s_pas",
    s_pas,
    "s_callpair",
    s_callpair,
    "s_nms",
    s_nms,
    "s_media_resource",
    s_media_resource
)
