from sqlalchemy import create_engine

def connect():
    engine = create_engine('mysql://exgensql:yKH2T&%u~L5<@localhost/ExGenDB')
    conn = engine.connect()
    trans = conn.begin()
    return conn, trans
