-- 1.删除域下的license、2.删除license详细信息
-- 机房不存在的情况下，该数据无效
-- 参数: domain_moid license_id
local domain_moid = ARGV[1]
local license_id = ARGV[2]

local domainLicenseKey = "domain:" .. domain_moid .. ":license"
redis.call("SREM", domainLicenseKey, license_id)

local licenseInfoKey = "license:" .. license_id .. ":info"
redis.call("DEL", licenseInfoKey)
redis.call("SREM", "licenses", license_id)
