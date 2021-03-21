""""luban数据库映射"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, SmallInteger, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


# 域信息, domain_type: 0, 核心域, 1, 平台域
class DomainInfo(Base):
    __tablename__ = 'domain_info'
    id = Column(Integer, primary_key=True)
    domain_moid = Column(String(40))
    domain_type = Column(Integer)


# 机房, 核心域下机房为核心域机房
class MachineRoomInfo(Base):
    __tablename__ = 'machine_room_info'
    id = Column(Integer, primary_key=True)
    machine_room_type = Column(Integer)
    machine_room_name = Column(String(128))
    machine_room_moid = Column(String(40))
    domain_moid = Column(String(40))
    frames = relationship('FrameInfo')


class MachineInfo(Base):
    __tablename__ = 'machine_info'
    id = Column(Integer, primary_key=True)
    machine_moid = Column('machine_moid', String(40), unique=True)
    machine_name = Column('machine_name', String(128))
    machine_type = Column('machine_type', String(40))
    machine_room_moid = Column('machine_room_moid', String(40))
    machine_room_name = Column('machine_room_name', String(128))
    mac_id = Column('mac_id', String(40))
    ips = relationship('IpInfo')


class IpInfo(Base):
    __tablename__ = 'ip_info'
    id = Column(Integer, primary_key=True)
    ip = Column(String(128), unique=True)
    flag = Column(Integer)
    machine_id = Column(Integer, ForeignKey('machine_info.id'))


class FrameInfo(Base):
    __tablename__ = 'frame_info'
    id = Column(Integer, primary_key=True)
    frame_name = Column(String(128))
    frame_type = Column(String(40))
    frame_moid = Column(String(40))
    machine_room_id = Column(Integer, ForeignKey('machine_room_info.id'))
    machine_room = relationship('MachineRoomInfo', back_populates='frames')


class PeripheralInfo(Base):
    __tablename__ = 'peripheral_info'
    id = Column(Integer, primary_key=True)
    per_type = Column(String(40))
    per_sub_type = Column(String(40))
    per_moid = Column(String(40))
    machine_room_moid = Column(String(40))


class PeripheralConfig(Base):
    __tablename__ = 'peripheral_config'
    id = Column(Integer, primary_key=True)
    key = Column(String(36))
    value = Column(String(128))
    peripheral_id = Column(Integer, ForeignKey('peripheral_info.id'))
    peripheral = relationship('PeripheralInfo')


class ServerInfo(Base):
    __tablename__ = 'server_info'
    id = Column(Integer, primary_key=True)
    p_server_moid = Column(String(40))
    server_type = Column(String(40))
    server_moid = Column(String(40))
    machine_room_moid = Column(String(40))
    server_name = Column(String(128))


class MachineInfoBak(Base):
    __tablename__ = 'machine_info_bak'
    id = Column(Integer, primary_key=True)
    # 0,add, 1,update, 2,delete
    operate = Column(Integer)
    machine_moid = Column(String(40))
    machine_name = Column(String(128))
    machine_type = Column(String(40))
    machine_room_moid = Column(String(40))
    machine_room_name = Column(String(128))
    mac_id = Column(String(40))
    ip = Column(String(128))


class ServerInfoBak(Base):
    __tablename__ = 'server_info_bak'
    id = Column(Integer, primary_key=True)
    operate = Column(Integer)
    p_server_moid = Column(String(40))
    server_type = Column(String(40))
    server_moid = Column(String(40))
    machine_room_moid = Column(String(40))
    server_name = Column(String(128))
