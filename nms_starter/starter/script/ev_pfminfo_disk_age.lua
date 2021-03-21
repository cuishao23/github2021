-- 磁盘寿命
-- 参数: moid, diskInfo

local moid = ARGV[1]
local diskInfo = cjson.decode(ARGV[2])
for name, age in pairs(diskInfo) do
    redis.call("ZADD", "disk_age", age, moid .. ":" .. name)
end

local diskCount = redis.call("HGET", "p_server:" .. moid .. ":resource", "disk_count")
for i = 1, tonumber(diskCount) do
    local name = redis.call("HGET", "p_server:" .. moid .. ":resource", "disk" .. i .. "_name")
    if diskInfo[name] then
        redis.call("HSET", "p_server:" .. moid .. ":resource", "disk" .. i .. "_age", diskInfo[name])
    end
end
