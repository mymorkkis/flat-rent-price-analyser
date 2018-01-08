DROP TABLE IF EXISTS flat_price_analysis;

CREATE TABLE flat_price_analysis (
	id SERIAL4 PRIMARY KEY,
	description VARCHAR(100),
	postcode_area VARCHAR(4),
	price INT,
	website VARCHAR(20),
	created_on DATE DEFAULT CURRENT_DATE
)