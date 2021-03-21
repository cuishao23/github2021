-- 1.添加license到域信息下、2.增加license详细信息
-- 参数: domain_moid license_id mcu_exp_date mac_id
local domain_moid = ARGV[1]
local license_id = ARGV[2]
local mcu_exp_date = ARGV[3]
local mac_id = ARGV[4]

local domainLicenseKey = "domain:" .. domain_moid .. ":license"
redis.call("SADD", domainLicenseKey, license_id)

local licenseInfoKey = "license:" .. license_id .. ":info"
redis.call('SADD', 'licenses', license_id)
redis.call("HMSET", licenseInfoKey, "mcu_exp_date", mcu_exp_date, "mac_id", mac_id)
