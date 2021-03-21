from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from functools import partial

from config import common


nms_engine = create_engine(
    common.MYSQL,
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=10,  # 连接池大小
    pool_timeout=30,
    pool_recycle=120
)

bmc_engine = create_engine(
    common.BMC_MYSQL,
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=10,  # 连接池大小
    pool_timeout=30,
    pool_recycle=120
)

luban_engine = create_engine(
    common.LUBAN_MYSQL,
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=10,  # 连接池大小
    pool_timeout=30,
    pool_recycle=120
)

NmsSession = sessionmaker(bind=nms_engine)
BmcSession = sessionmaker(bind=bmc_engine)
LubanSession = sessionmaker(bind=luban_engine)


# 使用上下文管理session
# with xxx_session_scope() as session:
#     pass
@contextmanager
def session_scope(maker):
    session = maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


nms_session_scope = partial(session_scope, maker=NmsSession)
bmc_session_scope = partial(session_scope, maker=BmcSession)
luban_session_scope = partial(session_scope, maker=LubanSession)

__all__ = ('nms_session_scope', 'bmc_session_scope', 'luban_session_scope')
