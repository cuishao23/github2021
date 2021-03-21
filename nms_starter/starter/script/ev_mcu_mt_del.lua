-- 终端离会
-- 参数: meetingType e164 mtType mtE164OrIP ...

-- 获取会议终端详情
local function getTerminalDetail(confE164, mtMoid)
    -- 基本信息: terminal:moid:meetingdetail
    -- 网络信息: terminal:moid:type:netinfo
    -- 名称和运营商: terminal:moid:baseinfo
    local terminalDetail = {}
    if confE164 == redis.call("HGET", "terminal:" .. mtMoid .. ":meetingdetail", "conf_e164") then
        local detailList = redis.call("HGETALL", "terminal:" .. mtMoid .. ":meetingdetail")
        for i = 1, #detailList / 2 do
            terminalDetail[detailList[i * 2 - 1]] = detailList[i * 2]
        end
        terminalDetail["mt_name"] = redis.call("HGET", "terminal:" .. mtMoid .. ":baseinfo", "name") or ""
        terminalDetail["operate"] = redis.call("HGET", "terminal:" .. mtMoid .. ":baseinfo", "operate_type") or ""
        local terminalType = terminalDetail["mt_type"]
        if terminalType then
            local netinfoKey = "terminal:" .. mtMoid .. ":" .. string.gsub(terminalType, " ", "~") .. ":netinfo"
            terminalDetail["ip"] = redis.call("HGET", netinfoKey, "ip") or ""
            terminalDetail["net_ip"] = redis.call("HGET", netinfoKey, "net_ip") or ""
        end

        -- 清除详情
        redis.call("DEL", "terminal:" .. mtMoid .. ":meetingdetail")
    end
    return terminalDetail
end

-- 记录终端离会
local addTerminalLeaveInfo = function(confE164, mtMoid, leaveTime, leaveReason)
    local enterTimesKey = "terminal:" .. mtMoid .. ":conf:" .. confE164 .. ":enter_times"
    local enterTimes = redis.call("GET", enterTimesKey)
    local enterLeaveInfoKey = "terminal:" .. mtMoid .. ":conf:" .. confE164 .. ":enter_leave_info:" .. enterTimes
    redis.call("HMSET", enterLeaveInfoKey, "leave_time", leaveTime, "leave_reason", leaveReason)
end

-- 设置终端状态为online
local setTerminalOnlineState = function(mtMoid, ip)
    local moid = mtMoid or redis.call("HGET", "terminal:ip2moid", ip)
    if moid then
        local onlineStateKey = "terminal:" .. moid .. ":onlinestate"
        for i, terminalType in pairs(redis.call("HKEYS", onlineStateKey)) do
            if "conference" == redis.call("HGET", onlineStateKey, terminalType) then
                redis.call("HSET", onlineStateKey, terminalType, "online")
            end
        end
    end
end

local meetingType = ARGV[1]
local e164 = ARGV[2]
local mtType = ARGV[3]
local mtE164OrIp = ARGV[4]
local result = {}

local meetingInfoKey = meetingType .. ":" .. e164 .. ":info"
-- 会议存在
if redis.call("EXISTS", meetingInfoKey) == 1 then
    local mtMoid = redis.call("HGET", "terminal:" .. mtE164OrIp .. ":baseinfo", "moid")
    if mtType == "e164_ip" and mtMoid then
        -- 软硬终端
        result = getTerminalDetail(e164, mtMoid)
        addTerminalLeaveInfo(e164, mtMoid, ARGV[5], ARGV[6])
    elseif mtType == "meeting" then
        redis.call("HDEL", "meeting:" .. e164 .. ":meeting", mtE164OrIp)
    else
        redis.call("SREM", "meeting:" .. e164 .. ":" .. mtType, mtE164OrIp)
    end
    setTerminalOnlineState(mtMoid, mtE164OrIp)
end

return string.gsub(cjson.encode(result), "{}", "[]")
