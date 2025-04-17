
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
  zone = Column(Integer)
  subzone = Column(Integer)
  site = Column(String)
  code_site = Column(String, unique=True)
  list_columns = ['country','department','municipality','populated_center','zone','subzone','site','code_site']


  def __init__(self,country,department,municipality,populated_center,zone,subzone,site,code_site):
    self.country = country
    self.department = department
    self.municipality = municipality
    self.populated_center = populated_center
    self.zone = zone
    self.subzone = subzone
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




# Botanical taxonomy table
class Taxonomy_details(Base):
    '''
    This table stores taxonomic information for plant species recorded in biodiversity datasets.
    It includes classification details, scientific naming, identification authority, conservation status,
    and optionally, the Plant Functional Type (PFT) used in ecological analyses.

    Columns:
    - id_taxonomy: Integer (Primary Key)
    - family: String
    - genus: String
    - specie: String
    - accept_scientific_name: String
    - gbif_id: String
    - lifeForm: String
    - establishmentMeans: String
    - pft_id: Integer (Functional classification for the species)
    - specie_functional_group: Integer
    - iucn_category: String
    - identified_by: String
    - date_of_identification: String (consider Date if consistent)
    '''

    __tablename__ = 'taxonomy_details'

    id_taxonomy = Column(Integer, primary_key=True)
    family = Column(String)
    genus = Column(String)
    specie = Column(String)
    accept_scientific_name = Column(String)
    gbif_id = Column(String)
    lifeForm = Column(String)
    origin = Column(String)
    use = Column(String)
    iucn_category = Column(String)
    identified_by = Column(String)
    date_of_identification = Column(String)

    biodiversity_records = relationship("Biodiversity_records", back_populates="taxonomy")
    structure_traits = relationship("FunctionalTraitsStructure", back_populates="taxonomy")

    list_columns = [
        'family', 'genus', 'specie', 'accept_scientific_name', 'gbif_id',
        'lifeForm', 'origin', 'use',
        'iucn_category', 'identified_by', 'date_of_identification'
    ]

    def __init__(self, family, genus, specie, accept_scientific_name,
                 gbif_id, lifeForm, origin, use,
                 iucn_category, identified_by, date_of_identification):
        self.family = family
        self.genus = genus
        self.specie = specie
        self.accept_scientific_name = accept_scientific_name
        self.gbif_id = gbif_id
        self.lifeForm = lifeForm
        self.origin = origin
        self.use = use
        self.iucn_category = iucn_category
        self.identified_by = identified_by
        self.date_of_identification = date_of_identification

    def __repr__(self):
        return f"<TaxonomyDetails({self.accept_scientific_name})>"

    def __str__(self):
        return self.accept_scientific_name



# Functional traits assigned per species
class FunctionalTraitsStructure(Base):
    '''
    This table stores both structural and functional trait data for plant species,
    grouped under Plant Functional Types (PFTs). It includes references to species taxonomy.

    Structural traits include observable features like canopy shape and color.
    Functional traits are quantitative measures such as height, shade index, or carbon capture.

    Columns:
    - id_structure: Integer (Primary Key)
    - pft_id: Integer
    - taxonomy_id: Integer (ForeignKey to taxonomy_details.id_taxonomy)
    - canopy_shape: String
    - color: String
    - carbon_sequestration_min/max: Float
    - shade_index_min/max: Float
    - canopy_diameter_min/max: Float
    - height_max_min/max: Float
    '''
    __tablename__ = 'functional_traits_structure'

    id_structure = Column(Integer, primary_key=True)
    pft_id = Column(Integer)
    species = Column(String)
    taxonomy_id = Column(Integer, ForeignKey("taxonomy_details.id_taxonomy"))
    taxonomy = relationship("Taxonomy_details", back_populates="structure_traits")

    # Structural traits
    canopy_shape = Column(String)
    color = Column(String)

    # Functional trait ranges
    carbon_sequestration_min = Column(Float)
    carbon_sequestration_max = Column(Float)

    shade_index_min = Column(Float)
    shade_index_max = Column(Float)

    canopy_diameter_min = Column(Float)
    canopy_diameter_max = Column(Float)

    height_max_min = Column(Float)
    height_max_max = Column(Float)

    

    list_columns = [
        'pft_id', 'species','taxonomy_id', 'canopy_shape', 'color',
        'carbon_sequestration_min', 'carbon_sequestration_max',
        'shade_index_min', 'shade_index_max',
        'canopy_diameter_min', 'canopy_diameter_max',
        'height_max_min', 'height_max_max'
    ]

    def __init__(self, pft_id,species , taxonomy_id, canopy_shape, color,
                 carbon_sequestration_min, carbon_sequestration_max,
                 shade_index_min, shade_index_max,
                 canopy_diameter_min, canopy_diameter_max,
                 height_max_min, height_max_max):
        self.pft_id = pft_id
        self.species = species
        self.taxonomy_id = taxonomy_id
        self.canopy_shape = canopy_shape
        self.color = color
        self.carbon_sequestration_min = carbon_sequestration_min
        self.carbon_sequestration_max = carbon_sequestration_max
        self.shade_index_min = shade_index_min
        self.shade_index_max = shade_index_max
        
        self.canopy_diameter_min = canopy_diameter_min
        self.canopy_diameter_max = canopy_diameter_max
        self.height_max_min = height_max_min
        self.height_max_max = height_max_max

    def __repr__(self):
        return f"<FunctionalTraitsStructure(taxonomy_id={self.taxonomy_id}, pft={self.pft_id})>"

    def __str__(self):
        return f"Species Taxonomy ID {self.taxonomy_id} – PFT {self.pft_id}"



# Biodiversity records table
class Biodiversity_records(Base):
  '''
  This table contains the biodiversity records and the most important data 
  collected in the field. It inherits its properties from the `Base` class 
  of the SQLAlchemy module. This table is related to taxonomy, geographic 
  coordinate systems, and location data via foreign keys.

  The columns and data types that this table requires are:

  code_record: String |This must be UNIQUE in the entire table| |Primary Key|
  common_name: String
  latitude: Float
  longitude: Float
  elevation_m: Float
  registered_by: String
  date_event: DateTime
  taxonomy_id: Integer |Foreign Key to taxonomy_details.id_taxonomy|
  place_id: Integer |Foreign Key to places.id_place|
  epsg_id: SmallInteger |Foreign Key to geog_coord_syst.epsg|
  '''
  __tablename__ = 'biodiversity_records'
  code_record = Column(Integer, nullable=False, unique=True, primary_key=True)
  common_name = Column(String)
  latitude = Column(Float)
  longitude = Column(Float)
  elevation_m = Column(Float)
  registered_by = Column(String)
  date_event = Column(DateTime)

  taxonomy_id = Column(Integer, ForeignKey("taxonomy_details.id_taxonomy"))
  taxonomy = relationship("Taxonomy_details", back_populates="biodiversity_records")

  place_id = Column(Integer, ForeignKey("places.id_place"))
  place = relationship("Place")

  epsg_id = Column(SmallInteger, ForeignKey("geog_coord_syst.epsg"))
  epsg = relationship("Geog_coord_syst")

  list_columns = ['code_record', 'common_name', 'latitude', 'longitude', 'elevation_m', 'registered_by', 'date_event', 'place_id', 'epsg_id', 'taxonomy_id']

  def __init__(self, code_record, common_name, latitude, longitude, elevation_m, registered_by, date_event, place_id, epsg_id, taxonomy_id):
    self.code_record = code_record
    self.common_name = common_name
    self.latitude = latitude
    self.longitude = longitude
    self.elevation_m = elevation_m
    self.registered_by = registered_by
    self.date_event = date_event
    self.place_id = place_id
    self.epsg_id = epsg_id
    self.taxonomy_id = taxonomy_id

  def __repr__(self):
    return "<biodiversity_records(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"

  def __str__(self):
    return self.code_record
    
# Table of biodiversity records registered in the main project


# Table of measuraments
class Measurements(Base):
  '''
  This table contains the measurements
  from biodiversity records, specifying the methods by which these values were obtained.
  It inherits its properties from the `Base` class of the SQLAlchemy module.
  The columns and data types required by this table are:

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
  measurement_unit = Column(String)
  measurement_date_event = Column(DateTime)
  record_code = Column(Integer, ForeignKey("biodiversity_records.code_record"))
  biodiversity = relationship("Biodiversity_records")
  list_columns = ['measurement_name','measurement_value','measurement_method','measurement_unit','measurement_date_event','record_code']

  def __init__(self,measurement_name,measurement_value,measurement_method,measurement_unit,measurement_date_event,record_code):
    self.measurement_name = measurement_name 
    self.measurement_value = measurement_value
    self.measurement_method = measurement_method
    self.measurement_unit = measurement_unit
    self.measurement_date_event = measurement_date_event
    self.record_code = record_code
  def __repr__(self):
    tt = "<measurements(" + ','.join([f"'{i}'" for i in self.list_columns]) + ")>"
    return tt 

  def __str__(self):
    return self.record_code







# Table of observations from biodiversity records 
class Observations_details(Base):
    """
    This table stores qualitative and quantitative observation data associated with biodiversity records.
    It includes descriptive assessments (e.g., physical condition, aesthetic value) and condition indexes 
    (e.g., foliage density, phytosanitary status), as well as multiple binary indicators and numeric scores 
    from standardized evaluation protocols.

    The table inherits from SQLAlchemy's `Base` class, and its structure is designed to ensure compatibility 
    with environmental monitoring systems, urban tree inventories, and ecological health assessments.

    The columns and their expected data types are:

    record_code: String (Foreign Key from biodiversity_records.code_record)
    biological_record_comments: Text
    reproductive_condition: String
    observations: String
    accompanying_collectors: String
    physical_condition: String
    foliage_density: String
    aesthetic_value: String
    growth_phase: String
    ed: String
    hc: String
    hcf: String
    general_state: String
    cre, crh, cra, coa, ce, civ, crt, crg, cap: String (binary condition flags)
    rd, dm, bbs, ab, pi, ph, pa, pd, pe, pp, po, r_vol, r_cr, r_ce: String (scored indicators)
    """
    __tablename__ = 'observations_details'

    id_observation = Column(Integer, primary_key=True)
    record_code = Column(Integer, ForeignKey('biodiversity_records.code_record'))

    # Textual / Descriptive Fields
    biological_record_comments = Column(Text)
    reproductive_condition = Column(String)
    observations = Column(String)
    accompanying_collectors = Column(String)

    # Qualitative Assessments
    physical_condition = Column(String)
    foliage_density = Column(String)
    aesthetic_value = Column(String)
    growth_phase = Column(String)
    ed = Column(String)  # estado del dosel
    hc = Column(String)  # condición fitosanitaria
    hcf = Column(String)  # condición fitosanitaria del follaje
    general_state = Column(String)  # estado general

    # Binary Condition Flags
    cre = Column(String)
    crh = Column(String)
    cra = Column(String)
    coa = Column(String)
    ce = Column(String)
    civ = Column(String)
    crt = Column(String)
    crg = Column(String)
    cap = Column(String)

    # Numeric Scores (pueden ser cast a integer si se desea)
    rd = Column(String)
    dm = Column(String)
    bbs = Column(String)
    ab = Column(String)
    pi = Column(String)
    ph = Column(String)
    pa = Column(String)
    pd = Column(String)
    pe = Column(String)
    pp = Column(String)
    po = Column(String)
    r_vol = Column(String)
    r_cr = Column(String)
    r_ce = Column(String)

    biodiversity = relationship("Biodiversity_records")

    list_columns = [
        'record_code', 'biological_record_comments', 'reproductive_condition', 'observations',
        'accompanying_collectors', 'physical_condition', 'foliage_density', 'aesthetic_value',
        'growth_phase', 'ed', 'hc', 'hcf', 'general_state',
        'cre', 'crh', 'cra', 'coa', 'ce', 'civ', 'crt', 'crg', 'cap',
        'rd', 'dm', 'bbs', 'ab', 'pi', 'ph', 'pa', 'pd', 'pe', 'pp', 'po',
        'r_vol', 'r_cr', 'r_ce'
    ]

    def __init__(self, **kwargs):
        for key in self.list_columns:
            setattr(self, key, kwargs.get(key))

    def __repr__(self):
        return f"<Observations_details(record_code='{self.record_code}')>"

    def __str__(self):
        return self.record_code

  


