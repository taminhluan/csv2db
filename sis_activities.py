# ignore this function, it is just used to generate test database
def make_db(connection_string):
    from sqlalchemy import Column, Integer, String, text, ForeignKey, Table, ForeignKeyConstraint, create_engine
    from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base

    # create Base
    Base = declarative_base()

    class Level1(Base):
        __tablename__ = 'level1_s'
        id = Column(Integer, primary_key=True)
        name = Column(String(10000))
    
    class Level2(Base):
        __tablename__ = 'level2'
        id = Column(Integer, primary_key=True)
        name = Column(String(10000))
        level1 = Column(Integer, ForeignKey('level1.id'))

    class Level3(Base):
        __tablename__ = 'level3'
        id = Column(Integer, primary_key=True)
        name = Column(String(10000))
        level2 = Column(Integer, ForeignKey('level2.id'))
    
    class Level4(Base):
        __tablename__ = 'level4'
        id = Column(Integer, primary_key=True)
        name = Column(String(10000))
        level3 = Column(Integer, ForeignKey('level3.id'))
    
    class Level5(Base):
        __tablename__ = 'level5'
        id = Column(Integer, primary_key=True)
        name = Column(String(10000))
        level4 = Column(Integer, ForeignKey('level4.id'))

    class Level5Value(Base):
        __tablename__ = 'level5_value'
        id = Column(Integer, primary_key=True)
        level5 = Column(Integer, ForeignKey('level5.id'))

    # create engine
    engine = create_engine(connection_string, echo=True)

    # create db session
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(bind=engine)
    db_session.commit()

########################################################################

from csv2db import csv2db

# connection string (used by sqlalchemy)
connection_string = 'postgresql+psycopg2://postgres:gfd%401245@128.199.172.190:15432/nrap'
# MySQL connection_string example. Beware of the charset
# connection_string = 'mysql://root:toor@localhost:3306/test?charset=utf8'

# create database if not exists (this is just for test case, you won't need this for real case)
# make_db(connection_string)


# the csv file name. If your worksheet is on "xls" format, please convert them into csv first (i.e: in MS Excel you can use File | Save As)
# the first line of the csv should be the header
file_name = 'sis_activities.csv'

# more info about csv_param: http://docs.python.org/2/library/csv.html#csv-fmt-params
csv_param = {
    'delimiter': ',',   # libre office usually use "," while microsoft office usually use "tab"
    'quotechar': '"'    # both, libre office and microsoft office usually use '"'
}

########################################################################

# define several preprocessing callbacks. These callbacks will be used to preprocess every cell based on it's column

def change_date_format(human_date):
    ''' change 08/31/2000 into 2000-08-31
    '''
    date_part = human_date.split('/')
    if len(date_part) == 3:
        day = date_part[1]
        month = date_part[0]
        year = date_part[2]
        computer_date = year + '-' + month + '-' + day
    else:
        computer_date = ''
    return computer_date

def remove_dollar(value):
    ''' remove $, computer doesn't understand $
    '''
    return float(value.replace('$', ''))

# callback dictionary. The key is caption of the column, the value is the function used
callback = {
    'Date' : change_date_format,
    'Price' : remove_dollar
}

########################################################################

# specific preprocess function (in case of 2 different fields refer to the same csv column)

def filter_qty(value):
    ''' get "1" as int from "1 bottle" string
    '''
    return int(value.split(' ')[0])

def filter_unit(value):
    ''' get "bottle" from "1 bottle"
    '''
    return ' '.join(value.split(' ')[1:])

########################################################################

# the table structure of your database and how they related to your csv file
# WARNING: "unique" doesn't has any correlation with database unique constraint, unique is used as csv record identifier (since primary key does not exists in csv)
# if you have many "unique" field, AND logic will be used to distinguish a field from another field
table_structure_list = [
    {
        'table_name' : 'activities',
        'column_list': {
            'id'    : {'primary': True},
            'sub_activity'  : {'caption': 'sub_activity'},
            'package'  : {'caption': 'package'},
            'activity_group'  : {'caption': 'activity_group'},
            'activity'  : {'caption': 'activity'},
            'collaborate_organization'  : {'caption': 'collaborate_organization'},
            'main_organization'  : {'caption': 'main_organization'},
            'unit'  : {'caption': 'unit'},
            'location'  : {'caption': 'location'},
            'time_range'  : {'caption': 'time_range'},
            'target'  : {'caption': 'target'}
        }
    },
]

# and here is the magic:
csv2db(file_name, csv_param, connection_string, table_structure_list, callback)