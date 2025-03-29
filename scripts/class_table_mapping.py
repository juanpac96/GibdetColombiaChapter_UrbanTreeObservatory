
# Author: Juan Pablo Cuevas Ing. Forest
# Github: https://github.com/juanpac96
# Copyright (c) 2022, legut Inc.  All rights reserved.
# Copyrights licensed under the New BSD License.
# See the accompanying LICENSE file for terms.

# Import the modules
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, SmallInteger
from sqlalchemy.orm import relationship

# Set specials function
def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                obj = constructor(*arg, **kw)
                session.add(obj)
        cache[key] = obj
        return obj

class UniqueMixin(object):
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return _unique(
                    session,
                    cls,
                    cls.unique_hash,
                    cls.unique_filter,
                    cls,
                    arg, kw
               )

# Set the initial parameters for make the databese

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/db_biodiversity', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define the tables that will be used in the database,
# With their respective names, relationships and data types by column

# Make the table of the projects


# Make the table of places

class Place(UniqueMixin, Base):
  '''
  The sites visited by the laboratory are defined in this table and NOT accept null values.
  It inherits its properties from the `Base` class of the SQLAlchemy module. 
  The columns and data types that this table requires are:

  id_place: Integer
  country: String
  department: String
  municipality: String
  populated_center: String
  site: String
  '''
  # Table name
  __tablename__ = 'places'
  # Table columns
  id_place = Column(Integer, primary_key=True)
  country = Column(String, nullable=False)
  department = Column(String, nullable=False)
  municipality = Column(String,  nullable=False)
  populated_center = Column(String)
  site = Column(String)
  code_site = Column(String, unique=True)
  list_columns = ['country','department','municipality','populated_center','site','code_site']


  def __init__(self,country,department,municipality,populated_center,site,code_site):
    self.country = country
    self.department = department
    self.municipality = municipality
    self.populated_center = populated_center
    self.site = site
    self.code_site =code_site

  def __repr__(self):
    return "<places(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"


  def __str__(self):
    return self.site
  # Put additionall methods for see if a site is unique in the table.
  @classmethod
  def unique_hash(cls, site):
    return site
  
  # Method for make a query
  @classmethod
  def unique_filter(cls, query, site):
    return query.filter(Place.site == site)

# Table of geografic systems

class Geog_coord_syst(Base):
  '''
  In this table is the information related to the georeferencing systems
  in which the coordinates indicated in the dataset were captured.
  It inherits its properties from the `Base` class of the SQLAlchemy module. 
  The columns and data types that this table requires are:

  epsg: SmallInteger
  unit: String
  geodetic_crs: String
  datum: String
  ellipsoid: String
  prime_meridian: String
  data_source: String
  information_source: String
  revision_date: DateTime
  scope: String
  area_of_use: String
  coordinate_system: String
  '''
  # Table name
  __tablename__ = 'geog_coord_syst'
  # Table columns
  epsg = Column(SmallInteger, primary_key=True)
  unit = Column(String)
  geodetic_crs = Column(String)
  datum = Column(String)
  ellipsoid = Column(String)
  prime_meridian = Column(String)
  data_source = Column(String)
  information_source = Column(String)
  revision_date = Column(DateTime)
  scope = Column(String)
  area_of_use = Column(String)
  coordinate_system = Column(String)
  list_columns = ['epsg','unit','geodetic_crs','datum','ellipsoid','prime_meridian',
                  'data_source','information_source','revision_date','scope',
                  'area_of_use','coordinate_system']

  def __init__(self, epsg, unit, geodetic_crs, datum, ellipsoid, prime_meridian, data_source,information_source, revision_date, scope, area_of_use, coordinate_system):
    self.epsg = epsg
    self.unit = unit
    self.geodetic_crs = geodetic_crs
    self.datum = datum
    self.ellipsoid = ellipsoid
    self.prime_meridian = prime_meridian
    self.data_source = data_source
    self.information_source = information_source
    self.revision_date = revision_date
    self.scope = scope
    self.area_of_use = area_of_use
    self.coordinate_system = coordinate_system
  def __repr__(self):
    return "<geog_coord_syst(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"


  def __str__(self):
    return self.epsg



# Table of biodiversity records registered in the main project
class Biodiversity_records(Base):
  '''
  This table has the information
  from the biodiversity records, and the most important data take from the field.
  It inherits its properties from the `Base` class of the SQLAlchemy module. 
  The columns and data types that this table requires are:

  code_record = String |This must to be UNIQUE in all table|
  species: String
  common_name: String
  habitat: String
  latitude: Float
  longitude: Float
  elevation_m: Float
  registered_by: String
  date_event:  DateTime
  project_id: Integer
  place_id: Integer
  epsg_id: SmallInteger
  '''
  # Table name
  __tablename__ = 'biodiversity_records'
  # Table columns
  code_record = Column(String, nullable=False, unique=True, primary_key=True)
  common_name = Column(String)
  latitude = Column(Float)
  longitude = Column(Float)
  elevation_m = Column(Float)
  registered_by = Column(String)
  date_event =  Column(DateTime)
  # In this section we implement the relation between the tables and their forgering keys.
  #project_id = Column(Integer, ForeignKey("projects.id_project"))
  #project = relationship("Project")
  place_id = Column(Integer, ForeignKey("places.id_place"))
  place = relationship("Place")
  epsg_id = Column(SmallInteger,ForeignKey("geog_coord_syst.epsg"))
  epsg = relationship("Geog_coord_syst")

  list_columns = ['code_record','common_name',
                   'latitude','longitude','elevation_m','registered_by','date_event','place_id','epsg_id'] #,'project_id'

  def __init__(self,code_record,common_name,habitat,
               latitude,longitude,elevation_m,registered_by,
               date_event,plot_id,place_id,epsg_id): #,project_id
    self.code_record = code_record
    self.common_name = common_name
    self.habitat = habitat
    self.latitude = latitude
    self.longitude = longitude
    self.elevation_m = elevation_m
    self.registered_by = registered_by
    self.date_event = date_event
    self.plot_id = plot_id
    self.place_id = place_id
    #self.project_id = project_id
    self.epsg_id = epsg_id



  def __repr__(self):
    return "<biodiversity_records(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>" 

  def __str__(self):
    return self.code_record

# Table of measuraments
class Measurements(Base):
  '''
  Esta tabla tiene las medidas.
  de los registros de biodiversidad, y especificando los metodos mediante los cuales se tomaron estos valores.
  Hereda sus propiedades de la clase `Base` del modulo SQLAlchemy.
  Las columnas y tipos de datos que requiere esta tabla son:

  measurement_name: String
  measurement_value: Float
  measurement_method: String
  measurement_date_event: DateTime
  record_code: String
  '''
  # Table name
  __tablename__ = "measurements"
  id_measurement = Column(Integer, primary_key=True)
  # Table columns
  measurement_name = Column(String(25))
  measurement_value = Column(Float)
  measurement_method = Column(String)
  measurement_date_event = Column(DateTime)
  record_code = Column(String, ForeignKey("biodiversity_records.code_record"))
  biodiversity = relationship("Biodiversity_records")
  list_columns = ['measurement_name','measurement_value','measurement_method','measurement_date_event','record_code']

  def __init__(self,measurement_name,measurement_value,measurement_method,measurement_date_event,record_code):
    self.measurement_name = measurement_name 
    self.measurement_value = measurement_value
    self.measurement_method = measurement_method
    self.measurement_date_event = measurement_date_event
    self.record_code = record_code
  def __repr__(self):
    tt = "<measurements(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"
    return tt 

  def __str__(self):
    return self.record_code




# Table of taxonomic botanic transformation
class Taxonomy_details(Base):
  '''
  This table has the taxonomic botanic category
  from the biodiversity records, and specifying the methods by which these values were taken.
  It inherits its properties from the `Base` class of the SQLAlchemy module. 
  The columns and data types that this table requires are:

  family: String
  genus: String
  specie: String
  accept_scientific_name: String
  record_code: String
  identified_by: String
  date_of_identification: DateTime
  '''
  # Table name
  __tablename__ = 'taxonomy_details'
  # Table columns
  id_taxonomy = Column(Integer, primary_key=True)
  family = Column(String)
  genus = Column(String)
  specie = Column(String)
  accept_scientific_name = Column(String)
  record_code = Column(String, ForeignKey('biodiversity_records.code_record'))
  identified_by = Column(String)
  date_of_identification =  Column(String)
  biodiversity = relationship("Biodiversity_records")
  list_columns = ['family', 'genus', 'specie','accept_scientific_name','record_code','identified_by','date_of_identification']
  
  def __init__(self,family, genus, specie,accept_scientific_name,record_code,identified_by,date_of_identification):
    self.family = family
    self.genus = genus
    self.specie = specie
    self.accept_scientific_name = accept_scientific_name
    self.record_code = record_code
    self.identified_by = identified_by
    self.date_of_identification = date_of_identification

  def __repr__(self):
    tt = "<taxonomy_details(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"
    return tt 

  def __str__(self):
    return self.record_code


# Table of observations from biodiversity records 
class Observations_details(Base):
  '''
  This table has the observations
  from the biodiversity records, and specifying the methods by which these values were taken.
  It inherits its properties from the `Base` class of the SQLAlchemy module. 
  The columns and data types that this table requires are:

  id_observation: Integer
  record_code: String
  biological_record_comments: String
  reproductive_condition: String
  observations String
  phytosanitary_status: String
  accompanying_collectors: String
  use: String
  '''
  # Table name
  __tablename__ = 'observations_details'
  # Table columns
  id_observation = Column(Integer, primary_key=True)
  record_code = Column(String, ForeignKey('biodiversity_records.code_record'))
  biological_record_comments  = Column(Text)
  reproductive_condition =  Column(String)
  observations = Column(String)
  phytosanitary_status = Column(String)
  accompanying_collectors = Column(String)
  use = Column(String)
  biodiversity = relationship("Biodiversity_records")
  # This is a atribute than contain the columns names
  list_columns = ['record_code','biological_record_comments','reproductive_condition','observations','phytosanitary_status','accompanying_collectors','use']

  def __init__(self, record_code,biological_record_comments,reproductive_condition,observations,phytosanitary_status,accompanying_collectors,use):
    self.record_code = record_code
    self.biological_record_comments = biological_record_comments
    self.reproductive_condition =reproductive_condition
    self.observations = observations
    self.phytosanitary_status = phytosanitary_status
    self.accompanying_collectors = accompanying_collectors
    self.use = use

  def __repr__(self):
    tt = "<observations_details(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"
    return tt 

  def __str__(self):
    return self.record_code
