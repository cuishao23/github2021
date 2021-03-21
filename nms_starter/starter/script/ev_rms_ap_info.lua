-- 接入端口资源
-- 参数 moid total used type

local moid = ARGV[1]
local total = ARGV[2]
local used = ARGV[3]
local serverType = ARGV[4]
local suffix
local key = nil
if serverType == "0" or serverType == 0 then
    suffix = moid .. ":ap"
else
    suffix = moid .. ":g_ap"
end

if redis.call("EXISTS", "domain:" .. moid .. ":info") == 1 then
    key = "domain:" .. suffix
elseif redis.call("EXISTS", "machine_room:" .. moid .. ":info") == 1 then
    key = "machine_room:" .. suffix
end

if key then
    redis.call("HMSET", key, "total", total, "used", used)
end
