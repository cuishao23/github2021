-- PAS上的终端在线详情
-- 参数: moid h323 sip monitor

local moid = ARGV[1]
local h323 = ARGV[2]
local sip = ARGV[3]
local monitor = ARGV[4]
local rtc = ARGV[5]
local maxCall = ARGV[6]
local curCall = ARGV[7]
local maxOnline = ARGV[8]
local curOnline = ARGV[9]

local lServerInfoKey = "l_server:" .. moid .. ":info"
local machineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid")

-- 机房下的pas moid信息
local machineRoomPasServerKey = "machine_room:" .. machineRoomMoid .. ":pas_server"
redis.call("SADD", machineRoomPasServerKey, moid)


-- 服务器在线信息
local pasOnlineKey = "pas:" .. moid .. ":online"
redis.call("HSET", pasOnlineKey, "h323", h323)
redis.call("HSET", pasOnlineKey, "sip", sip)
redis.call("HSET", pasOnlineKey, "monitor", monitor)
redis.call("HSET", pasOnlineKey, "rtc", rtc)
redis.call("HSET", pasOnlineKey, "max_call", maxCall)
redis.call("HSET", pasOnlineKey, "cur_call", curCall)
redis.call("HSET", pasOnlineKey, "max_online", maxOnline)
redis.call("HSET", pasOnlineKey, "cur_online", curOnline)


-- 阈值告警判定
local result = {}
result["callpair"] = redis.call("HGET", "warning:limit:global", "s_callpair")
result["pas"] = redis.call("HGET", "warning:limit:global", "s_pas")

return string.gsub(cjson.encode(result), "{}", "[]")
