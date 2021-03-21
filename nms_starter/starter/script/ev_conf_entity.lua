local userDomainMoid = ARGV[1]
local confId = ARGV[2]
local operation = ARGV[3]
local result = {}
if operation == "add" then
    redis.call("SADD", "domain:" .. userDomainMoid .. ":entity", confId)
    redis.call("HMSET", "entry:" .. confId .. ":info", "start_time", ARGV[4], "end_time", ARGV[5], "info", ARGV[6])
elseif operation == "update" then
    redis.call("HMSET", "entry:" .. confId .. ":info", "start_time", ARGV[4], "end_time", ARGV[5], "info", ARGV[6])
elseif operation == "delete" and redis.call("EXISTS", "entry:" .. confId .. ":info") == 1 then
    result["start_time"] = redis.call("HGET", "entry:" .. confId .. ":info", "start_time")
    result["end_time"] = redis.call("HGET", "entry:" .. confId .. ":info", "start_time")
    result["info"] = redis.call("HGET", "entry:" .. confId .. ":info", "info")
    redis.call("DEL", "entry:" .. confId .. ":info")
    redis.call("SREM", "domain:" .. confId .. ":entry")
end

return string.gsub(cjson.encode(result), "{}", "[]")
