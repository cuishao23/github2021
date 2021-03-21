""""bmc数据库映射"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, SmallInteger, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


# 服务域信息
class ServiceDomain(Base):
    __tablename__ = 'service_domain'
    service_domain_moid = Column(String(36), primary_key=True)
    service_domain_name = Column(String(128))
    parent_id = Column(String(36))


# 平台域信息(服务域为父级域)
class PlatformDomain(Base):
    __tablename__ = 'platform_domain'
    platform_domain_moid = Column(String(36), primary_key=True)
    platform_domain_name = Column(String(128))
    service_domain_moid = Column(String(36))


# 机房用户域关系
# 用户域仅关联单个机房
user_domain_machine_table = Table('user_domain_machine', Base.metadata,
                                  Column('user_domain_moid', String(
                                      36), ForeignKey('user_domain.user_domain_moid')),
                                  Column('machine_room_moid', String(
                                      36), ForeignKey('machine_room.machine_room_moid')))


# 用户域信息(服务域为父级域)
class UserDomain(Base):
    __tablename__ = 'user_domain'
    user_domain_moid = Column(String(36), primary_key=True)
    user_domain_name = Column(String(128))
    service_domain_moid = Column(String(36))
    machine_rooms = relationship(
        "MachineRoom",
        secondary=user_domain_machine_table,
        back_populates="user_domains")


# 机房信息
class MachineRoom(Base):
    __tablename__ = 'machine_room'
    machine_room_moid = Column(String(36), primary_key=True)
    machine_room_name = Column(String(128))
    platform_domain_moid = Column(String(36))
    user_domains = relationship(
        "UserDomain",
        secondary=user_domain_machine_table,
        back_populates="machine_rooms")


# license, 一个服务域可对应多个license, type=1为合并license, 无需导入
class LicenseInfo(Base):
    __tablename__ = 'license_info'
    service_domain_moid = Column(String(36), primary_key=True)
    license_id = Column(String(50), primary_key=True)
    mcu_exp_date = Column(Date())
    device_id = Column(String(180))
    type = Column(Integer)


# enable:账号启用禁用标识
class UserInfo(Base):
    __tablename__ = 'user_info'
    moid = Column(String(36), primary_key=True)
    account_type = Column(Integer)
    e164 = Column(String(48))
    user_domain_moid = Column(
        String(36), ForeignKey('user_domain.user_domain_moid'))
    service_domain_moid = Column(String(36))
    enable = Column(Integer)
    account = Column(String(128))
    email = Column(String(64))
    mobile = Column(String(64))
    user_profile = relationship(
        'UserProfile', uselist=False, back_populates='user_info')


class UserProfile(Base):
    __tablename__ = 'user_profile'
    moid = Column(String(36), ForeignKey('user_info.moid'), primary_key=True)
    name = Column(String(128))
    user_info = relationship('UserInfo', back_populates='user_profile')


# 老终端列表
class UserDomainAddressBookIp(Base):
    __tablename__ = 'user_domain_address_book_ip'
    moid = Column(String(36), primary_key=True)
    user_domain_moid = Column(
        String(36), ForeignKey('user_domain.user_domain_moid'))
    account = Column(String(128))
    name = Column(String(128))
    e164 = Column(String(48))


# 用户权限数据
class UserPrivilegeData(Base):
    __tablename__ = 'user_privilege_data'
    moid = Column(String(36), primary_key=True)
    setting_type = Column(String(50), primary_key=True)
    privilege_key = Column(String(30))
