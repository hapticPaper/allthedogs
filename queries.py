CREATE_DOGS = """
DROP TABLE IF EXISTS dogs;
CREATE TABLE IF NOT EXISTS dogs
(
	weight text,
	height text,
	id int not null
		constraint table_name_pk
			primary key,
	name text,
	bred_for text,
	breed_group text,
	life_span text,
	temperament text,
	origin text,
	country_code text,
	description text,
	history text,
	images text,
	img text
);
create unique index IF NOT EXISTS dogid on dogs (id);
"""

DOGS = """SELECT id, name, bred_for, breed_group, temperament, img
    FROM  dogs
    WHERE img != ''"""


def INSERT_DOG(data: list) -> str:
    return f"""INSERT INTO dogs
              VALUES({data})"""

DUMDOG = """INSERT INTO dogs
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"""