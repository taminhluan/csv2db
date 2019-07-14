# ignore this function, it is just used to generate test database
def make_db(connection_string):
    from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, ForeignKeyConstraint, create_engine, Float
    from sqlalchemy.orm import relationship, backref, scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base

    # create Base
    Base = declarative_base()
    class Family(Base):
        __tablename__ = 'family'
        id = Column(Integer, primary_key=True)
        name = Column(Text())

    class PlantPart(Base):
        __tablename__ = 'plant_part'
        id = Column(Integer, primary_key=True)
        name = Column(Text())

    class Compound(Base):
        __tablename__ = 'compound'
        id = Column(Integer, primary_key=True)
        name = Column(Text())
    

    class Plant(Base):
        __tablename__ = 'plant'
        id = Column(Integer, primary_key=True)
        scientific_name = Column(Text())
        synonym = Column(Text(collation='utf8_unicode_ci'))
        vietnamese_name = Column(Text(collation='utf8_unicode_ci'))
        family_id = Column(Integer, ForeignKey('family.id'))
        location = Column(Text(collation='utf8_unicode_ci'))
        description = Column(Text(collation='utf8_unicode_ci'))
        phenology = Column(Text(collation='utf8_unicode_ci'))
        habitat = Column(Text(collation='utf8_unicode_ci'))
        useto = Column(Text(collation='utf8_unicode_ci'))
        yields = Column(Text(collation='utf8_unicode_ci'))
    class PlantDetail(Base):
        __tablename__ = 'plant_detail'
        id = Column(Integer, primary_key=True)
        plant_id = Column(Integer, ForeignKey('plant.id'))
        plant_part_id = Column(Integer, ForeignKey('plant_part.id'))
        compound_id = Column(Integer, ForeignKey('compound.id'))
        percentage = Column(Float(11, 2))

    # create engine
    engine = create_engine(connection_string, echo=True)

    # create db session
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(bind=engine)
    db_session.commit()

########################################################################

from csv2db import csv2db

# connection string (used by sqlalchemy)
# connection_string = 'sqlite:///taynguyen.db'
# MySQL connection_string example. Beware of the charset
connection_string = 'mysql://root:gfdgfd@138.197.46.187:3306/gialaiplants?charset=utf8'

# create database if not exists (this is just for test case, you won't need this for real case)
make_db(connection_string)


# the csv file name. If your worksheet is on "xls" format, please convert them into csv first (i.e: in MS Excel you can use File | Save As)
# the first line of the csv should be the header
file_name = 'taynguyen.csv'

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
def preprocess_percentage(value):
    print('--'*40)
    print(value)
    print('--'*40)
    if value == '':
        print('???'*40)
        return None
    return value

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
        'table_name' : 'family',
        'column_list': {
            'id'    : {'primary': True},
            'name'  : {'caption': 'Family', 'unique': True}
        }
    },
    {
        'table_name' : 'compound',
        'column_list': {
            'id'    : {'primary': True},
            'name'  : {'caption': 'Major compounds', 'unique': True}
        }
    },
    {
        'table_name' : 'plant_part',
        'column_list': {
            'id'    : {'primary': True},
            'name'  : {'caption': 'Plant part', 'unique': True}
        }
    },
    {
        'table_name' : 'plant',
        'column_list': {
            'id'                : {'primary'  : True},
            'scientific_name'   : {'caption': 'Scientific Name', 'unique': True},
            'synonym'           : {'caption': 'Synonym'},
            'vietnamese_name'   : {'caption': 'Vietnamese name'},
            'family_id'         : {'reference': 'family.id', 'unique': True},
            'location'          : {'caption': 'Location'},
            'description'       : {'caption': 'Description'},
            'phenology'         : {'caption': 'Phenology'},
            'habitat'           : {'caption': 'Habitat'},
            'useto'               : {'caption': 'Use'},
            'yields'            : {'caption': 'Yield'}
        }
    },
    {
        'table_name'        : 'plant_detail',
        'column_list'       : {
            'id'                : {'primary'  : True},
            'plant_id'          : {'reference': 'plant.id', 'unique': True},
            'plant_part_id'     : {'reference': 'plant_part.id', 'unique': True},
            'compound_id'       : {'reference': 'compound.id', 'unique': True},
            'percentage'        : {'caption': 'Percentage'}
        }
    }
]

# and here is the magic:
csv2db(file_name, csv_param, connection_string, table_structure_list, callback)