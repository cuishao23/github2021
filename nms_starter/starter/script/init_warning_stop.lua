-- 暂停告警用户域/机房
-- 参数: num, moid1, moid2, moid3
local num = ARGV[1]
for i = 2, num + 1 do
    redis.call("SADD", "warning:stop", ARGV[i])
end
